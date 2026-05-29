def categorize_transaction_kz(description):
    desc = str(description).upper()

    # INCOME
    if any(x in desc for x in ['SALARY', 'SAL', 'PAYROLL', 'ЗАРПЛАТА',
                                 'ОКЛАД', 'KASPI SALARY', 'TRF FROM',
                                 'FTR FROM', 'HALYK', 'ПЕРЕВОД ОТ']):
        return 'Income'

    # FOOD & DINING
    if any(x in desc for x in ['GLOVO', 'WOLT', 'CHOCOFOOD', 'CHOPCHOP',
                                 'BURGER KING', 'KFC', 'MCDONALDS',
                                 'CHOCOTRAVEL', 'RESTAURANT', 'CAFE',
                                 'FOOD', 'КАФЕ', 'ЕДА', 'ДОСТАВКА']):
        return 'Food & Dining'

    # SHOPPING
    if any(x in desc for x in ['KASPI SHOP', 'WILDBERRIES', 'LAMODA',
                                 'SULPAK', 'TECHNODOM', 'MECHTA',
                                 'MAGNUM', 'SMALL', 'METRO CASH',
                                 'SHOPPING', 'МАГАЗИН', 'ПОКУПКА']):
        return 'Shopping'

    # TRANSPORT
    if any(x in desc for x in ['INDRIVE', 'YANDEX GO', 'YANDEX TAXI',
                                 'AIR ASTANA', 'FLY ARYSTAN', 'SCAT',
                                 'КАЗЖД', 'KTZ', 'KAZAKHSTAN RAILWAYS',
                                 'PETROL', 'FUEL', 'АЗС', 'БЕНЗИН',
                                 'TRANSPORT', 'ТАКСИ']):
        return 'Transport'

    # UTILITIES
    if any(x in desc for x in ['KCELL', 'BEELINE', 'TELE2', 'ACTIV',
                                 'ALTEL', 'KAZAKHTELECOM', 'КСЕЛЛ',
                                 'БИЛАЙН', 'ТЕЛЕ2', 'INTERNET',
                                 'ALMATY ENERGO', 'KEGOC', 'СВЕТА',
                                 'КОММУНАЛКА', 'ЖКХ', 'ВОДОКАНАЛ',
                                 'ELECTRICITY', 'UTILITY', 'BILL']):
        return 'Utilities'

    # HEALTHCARE
    if any(x in desc for x in ['HOSPITAL', 'CLINIC', 'PHARMACY',
                                 'БОЛЬНИЦА', 'АПТЕКА', 'ПОЛИКЛИНИКА',
                                 'MEDICALCENTER', 'INVIVO', 'OLYMPIC',
                                 'HEALTH', 'ДОКТОР', 'МЕДИЦИНА']):
        return 'Healthcare'

    # ENTERTAINMENT
    if any(x in desc for x in ['KINOPARK', 'CHAPLIN', 'CINEMAPARK',
                                 'NETFLIX', 'SPOTIFY', 'YOUTUBE',
                                 'КИНОПАРК', 'ЧАПЛИН', 'CINEMA',
                                 'GAME', 'ИГРЫ', 'РАЗВЛЕЧЕНИЯ']):
        return 'Entertainment'

    # EDUCATION
    if any(x in desc for x in ['UNIVERSITY', 'SCHOOL', 'КУРСЫ',
                                 'УНИВЕРСИТЕТ', 'КОЛЛЕДЖ', 'УЧЕБА',
                                 'EDUCATION', 'TUITION', 'DIPLOM',
                                 'COURSERA', 'UDEMY', 'SKILLBOX']):
        return 'Education'

    # LOAN & FINANCE
    if any(x in desc for x in ['LOAN', 'EMI', 'KASPI KREDIT',
                                 'КРЕДИТ', 'РАССРОЧКА', 'ЗАЙМ',
                                 'FINANCE', 'INSURANCE', 'СТРАХОВКА',
                                 'HALYK FINANCE', 'FREEDOM FINANCE']):
        return 'Loan & Finance'

    # TAX & GOVERNMENT
    if any(x in desc for x in ['TAX', 'НАЛОГ', 'ГОСПОШЛИНА',
                                 'EGOV', 'EGOV.KZ', 'ПРАВИТЕЛЬСТВО',
                                 'GOVERNMENT', 'ШТРАФ', 'FINE',
                                 'PENALTY', 'ЦОН']):
        return 'Tax & Government'

    # KASPI TRANSFER
    if any(x in desc for x in ['KASPI TRANSFER', 'KASPI PAY',
                                 'ПЕРЕВОД', 'TRANSFER', 'НЕФТ',
                                 'NEFT', 'IMPS', 'RTGS', 'TRF',
                                 'FTR TO', 'SWIFT']):
        return 'Transfer'

    # ATM & CASH
    if any(x in desc for x in ['ATM', 'CASH', 'БАНКОМАТ',
                                 'НАЛИЧНЫЕ', 'СНЯТИЕ', 'WITHDRAWAL']):
        return 'ATM & Cash'

    return 'Other'