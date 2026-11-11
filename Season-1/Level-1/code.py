
from collections import namedtuple
from decimal import Decimal

MAX_ITEM_AMOUNT = 100000
MAX_QUANTITY = 100
MIN_QUANTITY = 0
MAX_TOTAL = Decimal('1000000')

Order = namedtuple('Order', 'id, items')
Item = namedtuple('Item', 'type, description, amount, quantity')


def validorder(order: Order):
    payments = Decimal('0')
    expenses = Decimal('0')

    for item in order.items:
        if item.type == 'payment':
            if -MAX_ITEM_AMOUNT <= item.amount <= MAX_ITEM_AMOUNT:
                payments += Decimal(str(item.amount))

        elif item.type == 'product':
            if (
                type(item.quantity) is int
                and MIN_QUANTITY < item.quantity <= MAX_QUANTITY
                and MIN_QUANTITY < item.amount <= MAX_ITEM_AMOUNT
            ):
                expenses += Decimal(str(item.amount)) * item.quantity

        else:
            return "Invalid item type: %s" % item.type

    if abs(payments) > MAX_TOTAL or expenses > MAX_TOTAL:
        return "Total amount payable for an order exceeded"

    if payments != expenses:
        return "Order ID: %s - Payment imbalance: $%0.2f" % (
            order.id, payments - expenses
        )

    return "Order ID: %s - Full payment received!" % order.id
