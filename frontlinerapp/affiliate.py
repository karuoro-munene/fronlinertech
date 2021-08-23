from django.core.exceptions import ObjectDoesNotExist

from .models import UserTransactions, CustomUser, SystemTransactions, UserWallet, SystemWallet, Profile, UserReferees
from pinax.referrals.models import ReferralResponse

registration_fee = 3500

top_level_fee_to_system = registration_fee

middle_level_fee_to_system = registration_fee

bottom_level_fee_to_system = 500
bottom_level_fee_to_two_levels_up_referrer = 3000

lowest_level_fee_to_system = 250
lowest_level_fee_to_two_levels_up_referrer = 3000
lowest_level_fee_to_three_levels_up_referrer = 250

try:
    admin = CustomUser.objects.get(username="admin")
except:
    pass


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
    if level_three is not None:
        profile.three_levels_up_user = level_three
        profile.save()
    profile.save()
    return {"one_up": profile.one_level_up_user, "two_up": profile.two_levels_up_user,
            "three_up": profile.three_levels_up_user}


def compute_tree_quota(user):
    profiles = Profile.objects.all()
    user_referees_table = UserReferees.objects.get(user=user)
    tree_quota = []
    for profile in profiles:
        if user in [profile.one_level_up_user, profile.two_levels_up_user, profile.three_levels_up_user]:
            tree_quota.append(user)

        if user is profile.one_level_up_user:
            user_referees_table.level1.append(profile.user)
            user_referees_table.save()

        if user is profile.two_levels_up_user:
            user_referees_table.level2.append(profile.user)
            user_referees_table.save()

        if user is profile.three_levels_up_user:
            user_referees_table.level3.append(profile.user)
            user_referees_table.save()


def top_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=top_level_fee_to_system, type="INITIAL")
    system_transaction.save()

    try:
        system_wallet = SystemWallet.objects.get(user=admin)
    except:
        system_wallet = SystemWallet.objects.create(user=admin)
        system_wallet.save()

    if not system_wallet.initial_level_earnings is None:
        system_wallet.initial_level_earnings += top_level_fee_to_system
        system_wallet.total_balance += top_level_fee_to_system
    else:
        system_wallet.initial_level_earnings = top_level_fee_to_system
        system_wallet.total_balance = top_level_fee_to_system
    system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=top_level_fee_to_system, type="PAY")
    user_transaction.save()

    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()


def middle_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=middle_level_fee_to_system, type="ONE")
    system_transaction.save()

    system_wallet = SystemWallet.objects.get(user=admin)
    if not system_wallet.level_one_earnings is None:
        system_wallet.level_one_earnings += middle_level_fee_to_system
        system_wallet.total_balance += middle_level_fee_to_system
    else:
        system_wallet.level_one_earnings = middle_level_fee_to_system
        system_wallet.total_balance += middle_level_fee_to_system
    system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=middle_level_fee_to_system, type="PAY")
    user_transaction.save()

    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()


def bottom_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=bottom_level_fee_to_system, type="TWO")
    system_transaction.save()

    system_wallet = SystemWallet.objects.get(user=admin)
    if not system_wallet.level_two_earnings is None:
        system_wallet.level_two_earnings += bottom_level_fee_to_system
        system_wallet.total_balance += bottom_level_fee_to_system
    else:
        system_wallet.level_two_earnings = bottom_level_fee_to_system
        system_wallet.total_balance += bottom_level_fee_to_system
    system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=bottom_level_fee_to_system, type="PAY")
    user_transaction.save()

    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()

    # two levels up user earnings
    profile = Profile.objects.get(user=user)
    earner = profile.two_levels_up_user
    earner_wallet = UserWallet.objects.get(user=earner)
    #     add to their direct earnings
    if earner_wallet.direct_earnings is None:
        earner_wallet.direct_earnings = bottom_level_fee_to_two_levels_up_referrer
        earner_wallet.save()
    else:
        earner_wallet.direct_earnings += bottom_level_fee_to_two_levels_up_referrer
        earner_wallet.save()
    #     add to their total balance
    if earner_wallet.total_balance is None:
        earner_wallet.total_balance = bottom_level_fee_to_two_levels_up_referrer
        earner_wallet.save()
    else:
        earner_wallet.total_balance += bottom_level_fee_to_two_levels_up_referrer
        earner_wallet.save()


def lowest_level_transactions(user):
    system_transaction = SystemTransactions.objects.create(user=user, amount=lowest_level_fee_to_system, type="THREE")
    system_transaction.save()

    system_wallet = SystemWallet.objects.get(user=admin)
    if not system_wallet.level_three_earnings is None:
        system_wallet.level_three_earnings += lowest_level_fee_to_system
        system_wallet.total_balance += lowest_level_fee_to_system
        system_wallet.save()
    else:
        system_wallet.level_three_earnings = lowest_level_fee_to_system
        system_wallet.total_balance += lowest_level_fee_to_system
        system_wallet.save()

    user_transaction = UserTransactions.objects.create(user=user, amount=lowest_level_fee_to_system, type="PAY")
    user_transaction.save()

    user_wallet = UserWallet.objects.create(user=user)
    user_wallet.save()

    # two levels up user earnings
    profile = Profile.objects.get(user=user)
    level_two_earner = profile.two_levels_up_user
    level_two_earner_wallet = UserWallet.objects.get(user=level_two_earner)
    #     add to their direct earnings
    if level_two_earner_wallet.direct_earnings is None:
        level_two_earner_wallet.direct_earnings = lowest_level_fee_to_two_levels_up_referrer
        level_two_earner_wallet.save()
    else:
        level_two_earner_wallet.direct_earnings += lowest_level_fee_to_two_levels_up_referrer
        level_two_earner_wallet.save()
    #     add to their total balance
    if level_two_earner_wallet.total_balance is None:
        level_two_earner_wallet.total_balance = lowest_level_fee_to_two_levels_up_referrer
        level_two_earner_wallet.save()
    else:
        level_two_earner_wallet.total_balance += lowest_level_fee_to_two_levels_up_referrer
        level_two_earner_wallet.save()

        # three levels up user earnings
    level_three_earner = profile.three_levels_up_user
    level_three_earner_wallet = UserWallet.objects.get(user=level_three_earner)
    #     add to their direct earnings
    if level_three_earner_wallet.direct_earnings is None:
        level_three_earner_wallet.direct_earnings = lowest_level_fee_to_three_levels_up_referrer
        level_three_earner_wallet.save()
    else:
        level_three_earner_wallet.direct_earnings += lowest_level_fee_to_three_levels_up_referrer
        level_three_earner_wallet.save()
    #     add to their total balance
    if level_three_earner_wallet.total_balance is None:
        level_three_earner_wallet.total_balance = lowest_level_fee_to_three_levels_up_referrer
        level_three_earner_wallet.save()
    else:
        level_three_earner_wallet.total_balance += lowest_level_fee_to_three_levels_up_referrer
        level_three_earner_wallet.save()


def refresh_users_referees_tables():
    for user in CustomUser.objects.all():

        user_profile = Profile.objects.get(user=user)
        try:
            user_table = UserReferees.objects.get(user=user)
        except ObjectDoesNotExist:
            user_table = UserReferees.objects.create(user=user)

        for uu in CustomUser.objects.all():
            print(user)
            uu_profile = Profile.objects.get(user=uu)
            # print(uu_profile.one_level_up_user)
            # if uu is not user_profile.one_level_up_user:
            #     print(uu)
            #     user_table.level1.append(uu)
            #     user_table.save()


def implement_signup_money_flow(user):
    refresh_users_referees_tables()
    compute_tree_quota(user)
    compute_signup_money_flow(user)
    profile = Profile.objects.get(user=user)
    if profile.one_level_up_user is None and profile.two_levels_up_user is None and profile.three_levels_up_user is None:
        top_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is None and profile.three_levels_up_user is None:
        middle_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is not None and profile.three_levels_up_user is None:
        bottom_level_transactions(user)
    elif profile.one_level_up_user is not None and profile.two_levels_up_user is not None and profile.three_levels_up_user is not None:
        lowest_level_transactions(user)
