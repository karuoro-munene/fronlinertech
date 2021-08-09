from .models import UserTransactions, CustomUser, SystemTransactions, UserWallet, SystemWallet, Profile
from pinax.referrals.models import ReferralResponse

registration_fee = 3500

top_level_fee_to_system = registration_fee

middle_level_fee_to_system = registration_fee

bottom_level_fee_to_system = registration_fee - 500
bottom_level_fee_to_one_level_up_referrer = registration_fee - 3000

lowest_level_fee_to_system = registration_fee - 250
lowest_level_fee_to_two_levels_up_referrer = registration_fee - 3000
lowest_level_fee_to_one_level_up_referrer = registration_fee - 250



admin = CustomUser.objects.get(username="admin")


def get_upper_level_referrer(user):
    result = []
    for response in ReferralResponse.objects.all():
        if response.user == user:
            referral = response.referral
            one_level_up_user = referral.user
            result.append(one_level_up_user)
    try:
        return result[0]
    except IndexError:
        return None


def compute_signup_money_flow(user):
    profile = Profile.objects.get(user=user)
    level_one = get_upper_level_referrer(user)
    level_two = get_upper_level_referrer(level_one)
    level_three = get_upper_level_referrer(level_two)
    if level_one is not None:
        profile.one_level_up_user = level_one
        profile.save()
    if level_two is not None:
        profile.two_levels_up_user = level_two
        profile.save()
    if level_two is not None:
        profile.three_levels_up_user = level_three
        profile.save()


def top_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=registration_fee, type="INITIAL")
    system_transaction.save()

    try:
        system_wallet = SystemWallet.objects.get(user=admin)
    except:
        system_wallet = SystemWallet.objects.create(user=admin)
        system_wallet.save()

    if not system_wallet.level_one_earnings is None:
        system_wallet.level_one_earnings += registration_fee
        system_wallet.total_balance += registration_fee
    else:
        system_wallet.level_one_earnings = registration_fee
        system_wallet.total_balance = registration_fee
    system_wallet.save()
    user_transaction = UserTransactions.objects.create(user=user, amount=registration_fee, type="PAY")
    user_transaction.save()
    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()


def middle_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=registration_fee, type="ONE")
    system_transaction.save()

    try:
        system_wallet = SystemWallet.objects.get(user=admin)
    except:
        system_wallet = SystemWallet.objects.create(user=admin)
        system_wallet.save()

    if not system_wallet.level_one_earnings is None:
        system_wallet.level_one_earnings += registration_fee
        system_wallet.total_balance += registration_fee
    else:
        system_wallet.level_one_earnings = registration_fee
        system_wallet.total_balance = registration_fee
    system_wallet.save()
    user_transaction = UserTransactions.objects.create(user=user, amount=registration_fee, type="PAY")
    user_transaction.save()
    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()


def bottom_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=middle_level_fee_to_system, type="ONE")
    system_transaction.save()

    system_wallet = SystemWallet.objects.get(user=admin)
    if not system_wallet.level_two_earnings is None:
        system_wallet.level_two_earnings += middle_level_fee_to_system
        system_wallet.total_balance += middle_level_fee_to_system
        system_wallet.save()
    else:
        system_wallet.level_one_earnings = middle_level_fee_to_system
        system_wallet.total_balance += middle_level_fee_to_system
        system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=middle_level_fee_to_system, type="PAY")
    user_transaction.save()

    try:
        user_wallet = UserWallet.objects.get(user=user)
        user_wallet.save()
    except:
        user_wallet = UserWallet.objects.create(user=user)
        user_wallet.save()

    # one level up user earnings
    profile = Profile.objects.get(user)
    earner = profile.one_level_up_user
    earner_wallet = UserWallet.objects.get(user=earner)
    #     add to their direct earnings
    if earner_wallet.direct_earnings is None:
        earner_wallet.direct_earnings = middle_level_fee_to_one_level_up_referrer
        earner_wallet.save()
    else:
        earner_wallet.direct_earnings += middle_level_fee_to_one_level_up_referrer
        earner_wallet.save()
    #     add to their total balance
    if earner_wallet.total_balance is None:
        earner_wallet.total_balance = middle_level_fee_to_one_level_up_referrer
        earner_wallet.save()
    else:
        earner_wallet.total_balance += middle_level_fee_to_one_level_up_referrer
        earner_wallet.save()


def lowest_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=bottom_level_fee_to_system, type="THREE")
    system_transaction.save()

    system_wallet = SystemWallet.objects.get(user=admin)
    if not system_wallet.level_three_earnings is None:
        system_wallet.level_three_earnings += bottom_level_fee_to_system
        system_wallet.total_balance += bottom_level_fee_to_system
        system_wallet.save()
    else:
        system_wallet.level_one_earnings = bottom_level_fee_to_system
        system_wallet.total_balance += bottom_level_fee_to_system
        system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=bottom_level_fee_to_system, type="PAY")
    user_transaction.save()

    try:
        user_wallet = UserWallet.objects.get(user=user)
        user_wallet.save()
    except:
        user_wallet = UserWallet.objects.create(user=user)
        user_wallet.save()


def implement_signup_money_flow(user):
    compute_signup_money_flow(user)
    profile = Profile.objects.get(user=user)
    if profile.one_level_up_user is None:
        top_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is None:
        middle_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is not None and profile.three_levels_up_user is None:
        bottom_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is not None and profile.three_levels_up_user is not None:
        lowest_level_transactions(user)