import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class AuctionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.group_name = f'auction_{self.auction_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        state = await self.get_auction_state()
        await self.send(text_data=json.dumps({'type': 'state', **state}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'place_bid':
            user = self.scope['user']

            if not user or not user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You must be logged in to bid.'
                }))
                return

            result = await self.place_bid(data['amount'])

            if result['success']:
                payload = {
                    'type':        'bid_update',
                    'current_bid': result['current_bid'],
                    'bid_count':   result['bid_count'],
                    'bidder':      result['bidder'],
                    'amount':      result['amount'],
                    'time':        result['time'],
                }

                # ── Broadcast to all clients in this auction room ──────────
                # InMemoryChannelLayer: group_send works fine within a single
                # daphne/uvicorn process (one worker). Only breaks across
                # multiple processes — use Redis for multi-process production.
                await self.channel_layer.group_send(self.group_name, payload)

                # ── Also send a personal success confirmation directly back
                # to the bidder. This guarantees they see it even if
                # group_send has a race condition in dev. ─────────────────
                await self.send(text_data=json.dumps({
                    'type':    'bid_success',
                    'message': f'✅ Your bid of ₹{result["amount"]} was placed successfully!',
                    'amount':  result['current_bid'],
                }))

            else:
                await self.send(text_data=json.dumps({
                    'type':    'error',
                    'message': result['message'],
                }))

    # ── Group message handlers ─────────────────────────────────────────────────

    async def bid_update(self, event):
        await self.send(text_data=json.dumps({
            'type':        'bid_update',
            'current_bid': event['current_bid'],
            'bid_count':   event['bid_count'],
            'bidder':      event['bidder'],
            'amount':      event['amount'],
            'time':        event['time'],
        }))

    async def auction_ended(self, event):
        await self.send(text_data=json.dumps({'type': 'auction_ended'}))

    # ── DB helpers ─────────────────────────────────────────────────────────────

    @database_sync_to_async
    def get_auction_state(self):
        from auction.models import Auction
        try:
            auction  = Auction.objects.get(pk=self.auction_id)
            top_bids = list(
                auction.bids.order_by('-amount')
                .values('bidder__username', 'amount', 'placed_at')[:8]
            )
            for b in top_bids:
                b['amount']    = str(b['amount'])
                b['placed_at'] = b['placed_at'].strftime('%d %b %H:%M')
            return {
                'current_bid':    str(auction.highest_bid()),
                'bid_count':      auction.bid_count(),
                'time_remaining': auction.time_remaining(),
                'status':         auction.status,
                'recent_bids':    top_bids,
            }
        except Auction.DoesNotExist:
            return {}

    @database_sync_to_async
    def place_bid(self, amount):
        from auction.models import Auction, Bid
        from decimal import Decimal, InvalidOperation
        from django.db import transaction

        user = self.scope['user']
        try:
            with transaction.atomic():
                auction = Auction.objects.select_for_update().get(pk=self.auction_id)
                auction.check_and_end()

                if not auction.is_active():
                    return {'success': False, 'message': 'This auction has already ended.'}
                if auction.seller == user:
                    return {'success': False, 'message': 'You cannot bid on your own listing.'}

                try:
                    amount = Decimal(str(amount))
                except InvalidOperation:
                    return {'success': False, 'message': 'Invalid bid amount.'}

                current_high = auction.highest_bid()
                if amount <= current_high:
                    return {
                        'success': False,
                        'message': f'Bid must be higher than ₹{current_high}.',
                    }

                bid = Bid.objects.create(auction=auction, bidder=user, amount=amount)
                auction.current_bid = amount
                auction.save(update_fields=['current_bid'])

                return {
                    'success':     True,
                    'current_bid': str(amount),
                    'bid_count':   auction.bid_count(),
                    'bidder':      user.username,
                    'amount':      str(amount),
                    'time':        bid.placed_at.strftime('%d %b %H:%M'),
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}