from datetime import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_UP


class SymbolInfo:
    def __init__(self, symbol, filters):
        self.symbol = symbol

        self.minNotional = Decimal(self.strip_zeros(filters['MIN_NOTIONAL']['minNotional']))
        self.stepSize = Decimal(self.strip_zeros(filters['LOT_SIZE']['stepSize']))
        self.maxQty = Decimal(self.strip_zeros(filters['LOT_SIZE']['maxQty']))
        self.minQty = Decimal(self.strip_zeros(filters['LOT_SIZE']['minQty']))

        self.tickSize = Decimal(self.strip_zeros(filters['PRICE_FILTER']['tickSize']))
        self.maxPrice = Decimal(self.strip_zeros(filters['PRICE_FILTER']['maxPrice']))
        self.minPrice = Decimal(self.strip_zeros(filters['PRICE_FILTER']['minPrice']))

        self.multipUp = Decimal(self.strip_zeros(filters['PERCENT_PRICE']['multiplierUp']))
        self.multipDown = Decimal(self.strip_zeros(filters['PERCENT_PRICE']['multiplierDown']))


    # def __init__(self, minPrice, maxPrice, tickSize, minQty, maxQty, stepSize, minNotional, **kvargs):
    #     self.minNotional = Decimal(self.strip_zeros(minNotional))
    #     self.stepSize = Decimal(self.strip_zeros(stepSize))
    #     self.maxQty = Decimal(self.strip_zeros(maxQty))
    #     self.minQty = Decimal(self.strip_zeros(minQty))
    #     self.tickSize = Decimal(self.strip_zeros(tickSize))
    #     self.maxPrice = Decimal(self.strip_zeros(maxPrice))
    #     self.minPrice = Decimal(self.strip_zeros(minPrice))

    def strip_zeros(self, s):
        return s.rstrip('0')

    def adjust_quanity(self, q, round_down=True):
        if q == 0:
            return 0

        res = float(Decimal(q) if self.stepSize == 0.0 else Decimal(q).quantize(self.stepSize, rounding=ROUND_DOWN if round_down else ROUND_UP))
        return float(min(max(res, self.minQty), self.maxQty))

    def adjust_price(self, p, round_down=True):
        res = round(Decimal(p), 8)

        if self.tickSize:  # if tickSize Enabled
            res = res.quantize(self.tickSize, rounding=ROUND_DOWN if round_down else ROUND_UP)

        if self.minPrice:  # if minPrice Enabled
            res = max(res, self.minPrice)

        if self.maxPrice:  # if minPrice Enabled
            res = min(res, self.maxPrice)

        return float(res)

    def is_quanity_above_min(self, q):
        return q > self.minQty

    def is_min_notional_ok(self, q, p):
        return q * p >= self.minNotional

    def is_within_multiplier_range(self, p, current_price):
        return current_price * float(self.multipDown) <= p <= current_price * float(self.multipUp)

    def msg_mutliplier_range_error(self, current_price):
        return 'Price can not be lower thant {:.8f} and higher than {:.8f}.'\
            .format(current_price * float(self.multipDown), current_price * float(self.multipUp))


class ExchangeInfo:
    __shared_state = {}
    UPDATE_RATE_S = 30

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__dict__:
            self.symbols = {}
            self.last_updated = None

    def need_update(self):
        if not self.last_updated:
            return True

        return (datetime.now() - self.last_updated).seconds >= ExchangeInfo.UPDATE_RATE_S

    def update(self, info):
        self.symbols = {s['symbol']: s for s in info['symbols']}
        self.last_updated = datetime.now()

    def symbol_info(self, symbol):
        symbol_info = self.symbols.get(symbol)

        props = {}
        if symbol_info is None:
            raise KeyError('Symbol "{}" not found in the Exchnage makrets info'.format(symbol))

        for f in symbol_info['filters']:
            filter_type = f['filterType']
            f.pop(filter_type, None)
            props[filter_type] = f

        return SymbolInfo(symbol, props)

    def has_symbol(self, symbol):
        return symbol in self.symbols

    def get_all_symbols(self):
        return [{'s': s, 'b': info['baseAsset']} for (s, info) in self.symbols.items()]
