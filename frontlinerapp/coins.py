from django.core.exceptions import ObjectDoesNotExist
from frontlinerapp.models import CustomUser, Coins
from frontlinerapp.payments import pay_system


def buy_coins_from_admin(user, coins, phone_number):
    available_coins = Coins.objects.filter(user=None).count()
    if int(coins) <= available_coins:
        if pay_system(user, phone_number):
            data = {}
            user_coins = Coins.objects.filter(user=None)[:int(coins)]
            for coin in user_coins:
                coin.user = user
                coin.user_coins = True
                coin.save()
                data[coin.id] = coin.uuid
            return data
        else:
            print('Payment unsuccessful')
            return None
    else:
        print('Not enough coins to sell')
        return None







    return None


def buy_coins_from_users(buyer, seller):
    return None


def sell_coins(buyer, seller):
    return None