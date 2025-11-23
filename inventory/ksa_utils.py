"""
KSA (Saudi Arabia) Utility Functions
Helper functions for KSA compliance including:
- ZATCA E-Invoicing QR code generation
- VAT number validation
- Hijri calendar conversion
- HS code validation
"""
import base64
from struct import pack
from decimal import Decimal
import re
from datetime import date


# ==================== ZATCA E-Invoicing (Fatoora) ====================

def generate_zatca_qr_code(seller_name, vat_number, timestamp, total_with_vat, vat_amount):
    """
    Generate ZATCA-compliant QR code data for E-Invoicing (Fatoora).

    Args:
        seller_name (str): Company name (Arabic or English)
        vat_number (str): 15-digit VAT registration number
        timestamp (str): Invoice timestamp in ISO format (e.g., '2025-11-23T15:30:00Z')
        total_with_vat (Decimal/float): Total amount including VAT
        vat_amount (Decimal/float): VAT amount

    Returns:
        str: Base64-encoded QR code data string

    Example:
        >>> qr_data = generate_zatca_qr_code(
        ...     seller_name="شركة التصنيع المحدودة",
        ...     vat_number="300012345600003",
        ...     timestamp="2025-11-23T15:30:00Z",
        ...     total_with_vat=1150.00,
        ...     vat_amount=150.00
        ... )
        >>> print(qr_data)
        'AQkxMjMgRHJpbGxpbmcgQ28uAg8zMDAwMTIzNDU2MDAwMDMDFDIwMjUtMTEtMjNUMTU6MzA6MDBaBAgxMTUwLjAwBQc...'
    """

    def tlv_encode(tag, value):
        """
        Encode a value using TLV (Tag-Length-Value) format.

        Args:
            tag (int): Tag number (1-5 for Fatoora Phase 1)
            value (str): Value to encode

        Returns:
            bytes: Encoded bytes
        """
        value_bytes = value.encode('utf-8')
        length = len(value_bytes)
        return pack('B', tag) + pack('B', length) + value_bytes

    # Build TLV data structure
    tlv_data = b''

    # Tag 1: Seller name
    tlv_data += tlv_encode(1, seller_name)

    # Tag 2: VAT registration number
    tlv_data += tlv_encode(2, vat_number)

    # Tag 3: Timestamp
    tlv_data += tlv_encode(3, timestamp)

    # Tag 4: Total with VAT
    tlv_data += tlv_encode(4, f"{float(total_with_vat):.2f}")

    # Tag 5: VAT amount
    tlv_data += tlv_encode(5, f"{float(vat_amount):.2f}")

    # Base64 encode the TLV data
    qr_code_data = base64.b64encode(tlv_data).decode('utf-8')

    return qr_code_data


def decode_zatca_qr_code(qr_code_data):
    """
    Decode ZATCA QR code data back to readable format.
    Useful for verification and debugging.

    Args:
        qr_code_data (str): Base64-encoded QR code string

    Returns:
        dict: Decoded data with keys: seller_name, vat_number, timestamp, total_with_vat, vat_amount
    """
    try:
        # Decode base64
        tlv_bytes = base64.b64decode(qr_code_data)

        result = {}
        position = 0

        tag_names = {
            1: 'seller_name',
            2: 'vat_number',
            3: 'timestamp',
            4: 'total_with_vat',
            5: 'vat_amount'
        }

        while position < len(tlv_bytes):
            # Read tag
            tag = tlv_bytes[position]
            position += 1

            # Read length
            length = tlv_bytes[position]
            position += 1

            # Read value
            value_bytes = tlv_bytes[position:position + length]
            value = value_bytes.decode('utf-8')
            position += length

            # Store in result
            if tag in tag_names:
                result[tag_names[tag]] = value

        return result

    except Exception as e:
        return {'error': str(e)}


# ==================== VAT Number Validation ====================

def validate_saudi_vat_number(vat_number):
    """
    Validate Saudi Arabian VAT/TRN number format.

    Format: 15 digits, starting with 3
    Example: 300012345600003

    Args:
        vat_number (str): VAT number to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not vat_number:
        return False, "VAT number is required"

    # Remove spaces, hyphens, and other separators
    vat_clean = re.sub(r'[\s\-]', '', vat_number)

    # Check if it's exactly 15 digits
    if len(vat_clean) != 15:
        return False, f"VAT number must be 15 digits (got {len(vat_clean)})"

    # Check if it's all numeric
    if not vat_clean.isdigit():
        return False, "VAT number must contain only digits"

    # Check if it starts with 3
    if not vat_clean.startswith('3'):
        return False, "VAT number must start with 3"

    # Last two digits are check digits - basic validation passed
    return True, None


def format_saudi_vat_number(vat_number):
    """
    Format Saudi VAT number with hyphens for display.

    Args:
        vat_number (str): 15-digit VAT number

    Returns:
        str: Formatted VAT number (e.g., '300-0123-4560-0003')
    """
    vat_clean = re.sub(r'[\s\-]', '', vat_number)

    if len(vat_clean) == 15:
        return f"{vat_clean[0:3]}-{vat_clean[3:7]}-{vat_clean[7:11]}-{vat_clean[11:15]}"

    return vat_number


# ==================== Hijri Calendar ====================

def gregorian_to_hijri(gregorian_date):
    """
    Convert Gregorian date to Hijri (Islamic) date.
    Uses hijri-converter library.

    Args:
        gregorian_date (date): Gregorian date object

    Returns:
        str: Hijri date in format 'DD/MM/YYYY'
    """
    try:
        from hijri_converter import Gregorian

        g = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        )
        h = g.to_hijri()

        return f"{h.day:02d}/{h.month:02d}/{h.year}"

    except ImportError:
        # If hijri-converter not installed, return placeholder
        return "N/A (install hijri-converter)"

    except Exception as e:
        return f"Error: {str(e)}"


def get_hijri_month_name(month_number, language='ar'):
    """
    Get Hijri month name in Arabic or English.

    Args:
        month_number (int): Month number (1-12)
        language (str): 'ar' for Arabic, 'en' for English

    Returns:
        str: Month name
    """
    months_arabic = {
        1: 'محرم',
        2: 'صفر',
        3: 'ربيع الأول',
        4: 'ربيع الآخر',
        5: 'جمادى الأولى',
        6: 'جمادى الآخرة',
        7: 'رجب',
        8: 'شعبان',
        9: 'رمضان',
        10: 'شوال',
        11: 'ذو القعدة',
        12: 'ذو الحجة',
    }

    months_english = {
        1: 'Muharram',
        2: 'Safar',
        3: 'Rabi al-Awwal',
        4: 'Rabi al-Thani',
        5: 'Jumada al-Ula',
        6: 'Jumada al-Akhirah',
        7: 'Rajab',
        8: 'Shaban',
        9: 'Ramadan',
        10: 'Shawwal',
        11: 'Dhu al-Qidah',
        12: 'Dhu al-Hijjah',
    }

    if language == 'ar':
        return months_arabic.get(month_number, str(month_number))
    else:
        return months_english.get(month_number, str(month_number))


def format_hijri_date(hijri_date_str, language='ar'):
    """
    Format Hijri date with month name.

    Args:
        hijri_date_str (str): Hijri date in 'DD/MM/YYYY' format
        language (str): 'ar' for Arabic, 'en' for English

    Returns:
        str: Formatted date (e.g., '21 جمادى الأولى 1447' or '21 Jumada al-Ula 1447')
    """
    try:
        parts = hijri_date_str.split('/')
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])

        month_name = get_hijri_month_name(month, language)

        return f"{day} {month_name} {year}"

    except:
        return hijri_date_str


# ==================== HS Code Validation ====================

def validate_hs_code(hs_code, length=10):
    """
    Validate HS (Harmonized System) code format.
    Saudi Arabia uses 10-digit HS codes.

    Args:
        hs_code (str): HS code to validate
        length (int): Expected length (default 10 for Saudi Arabia)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not hs_code:
        return False, "HS code is required"

    # Remove spaces and dots
    hs_clean = re.sub(r'[\s\.]', '', hs_code)

    # Check if all characters are digits
    if not hs_clean.isdigit():
        return False, "HS code must contain only digits"

    # Check length
    if len(hs_clean) != length:
        return False, f"HS code must be {length} digits (got {len(hs_clean)})"

    return True, None


def format_hs_code(hs_code):
    """
    Format HS code with dots for readability.
    Example: 8207130000 -> 8207.13.00.00

    Args:
        hs_code (str): 10-digit HS code

    Returns:
        str: Formatted HS code
    """
    hs_clean = re.sub(r'[\s\.]', '', hs_code)

    if len(hs_clean) == 10:
        return f"{hs_clean[0:4]}.{hs_clean[4:6]}.{hs_clean[6:8]}.{hs_clean[8:10]}"

    return hs_code


# ==================== VAT Calculation ====================

def calculate_vat_amount(amount, vat_rate=Decimal('0.15')):
    """
    Calculate VAT amount from base amount.

    Args:
        amount (Decimal): Base amount (excluding VAT)
        vat_rate (Decimal): VAT rate (default 0.15 for 15%)

    Returns:
        Decimal: VAT amount
    """
    return amount * vat_rate


def calculate_amount_including_vat(amount, vat_rate=Decimal('0.15')):
    """
    Calculate total amount including VAT.

    Args:
        amount (Decimal): Base amount (excluding VAT)
        vat_rate (Decimal): VAT rate (default 0.15 for 15%)

    Returns:
        Decimal: Total amount including VAT
    """
    return amount * (Decimal('1') + vat_rate)


def extract_vat_from_total(total_with_vat, vat_rate=Decimal('0.15')):
    """
    Extract VAT amount from a total that includes VAT.

    Args:
        total_with_vat (Decimal): Total amount including VAT
        vat_rate (Decimal): VAT rate (default 0.15 for 15%)

    Returns:
        tuple: (base_amount, vat_amount)
    """
    base_amount = total_with_vat / (Decimal('1') + vat_rate)
    vat_amount = total_with_vat - base_amount

    return base_amount, vat_amount


# ==================== Zakat Calculation ====================

def calculate_zakat(zakatable_assets, zakat_rate=Decimal('0.025')):
    """
    Calculate Zakat amount.
    Zakat is 2.5% of zakatable assets (cash, inventory, receivables, etc.)

    Args:
        zakatable_assets (Decimal): Total zakatable assets
        zakat_rate (Decimal): Zakat rate (default 0.025 for 2.5%)

    Returns:
        Decimal: Zakat amount
    """
    return zakatable_assets * zakat_rate


# ==================== Saudi Postal Code Validation ====================

def validate_saudi_postal_code(postal_code):
    """
    Validate Saudi Arabian postal code format.
    Format: 5 digits (e.g., 12345)

    Args:
        postal_code (str): Postal code to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not postal_code:
        return False, "Postal code is required"

    # Remove spaces and hyphens
    postal_clean = re.sub(r'[\s\-]', '', postal_code)

    # Check if it's 5 digits
    if len(postal_clean) != 5:
        return False, f"Postal code must be 5 digits (got {len(postal_clean)})"

    # Check if all numeric
    if not postal_clean.isdigit():
        return False, "Postal code must contain only digits"

    return True, None


# ==================== Saudi Phone Number Validation ====================

def validate_saudi_phone_number(phone_number):
    """
    Validate Saudi Arabian phone number format.
    Formats accepted:
    - 05XXXXXXXX (mobile)
    - +9665XXXXXXXX (mobile with country code)
    - 01XXXXXXX (landline)

    Args:
        phone_number (str): Phone number to validate

    Returns:
        tuple: (is_valid, error_message, phone_type)
    """
    if not phone_number:
        return False, "Phone number is required", None

    # Remove spaces, hyphens, and parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone_number)

    # Mobile number patterns
    mobile_pattern_1 = re.compile(r'^05\d{8}$')  # 05XXXXXXXX
    mobile_pattern_2 = re.compile(r'^\+9665\d{8}$')  # +9665XXXXXXXX
    mobile_pattern_3 = re.compile(r'^9665\d{8}$')  # 9665XXXXXXXX

    # Landline pattern
    landline_pattern = re.compile(r'^0[1-4]\d{7}$')  # 01XXXXXXX, 02XXXXXXX, etc.

    if mobile_pattern_1.match(phone_clean) or mobile_pattern_2.match(phone_clean) or mobile_pattern_3.match(phone_clean):
        return True, None, 'mobile'
    elif landline_pattern.match(phone_clean):
        return True, None, 'landline'
    else:
        return False, "Invalid Saudi phone number format", None


def format_saudi_phone_number(phone_number, include_country_code=False):
    """
    Format Saudi phone number for display.

    Args:
        phone_number (str): Phone number to format
        include_country_code (bool): Whether to include +966 prefix

    Returns:
        str: Formatted phone number
    """
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone_number)

    # Remove leading 966 or 0 if present
    if phone_clean.startswith('966'):
        phone_clean = phone_clean[3:]
    elif phone_clean.startswith('0'):
        phone_clean = phone_clean[1:]

    # Format mobile number
    if len(phone_clean) == 9 and phone_clean[0] == '5':
        if include_country_code:
            return f"+966 {phone_clean[0]} {phone_clean[1:4]} {phone_clean[4:8]} {phone_clean[8:]}"
        else:
            return f"0{phone_clean[0]} {phone_clean[1:4]} {phone_clean[4:8]} {phone_clean[8:]}"

    # Format landline number
    elif len(phone_clean) == 8 and phone_clean[0] in '1234':
        if include_country_code:
            return f"+966 {phone_clean[0]} {phone_clean[1:4]} {phone_clean[4:]}"
        else:
            return f"0{phone_clean[0]} {phone_clean[1:4]} {phone_clean[4:]}"

    return phone_number


# ==================== Arabic Number Conversion ====================

def convert_to_arabic_numerals(number_str):
    """
    Convert Western numerals (0-9) to Arabic-Indic numerals (٠-٩).

    Args:
        number_str (str): String containing numbers

    Returns:
        str: String with Arabic-Indic numerals
    """
    arabic_numerals = {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩',
    }

    result = number_str
    for western, arabic in arabic_numerals.items():
        result = result.replace(western, arabic)

    return result


def format_currency_arabic(amount):
    """
    Format currency amount for Arabic display.

    Args:
        amount (Decimal/float): Amount to format

    Returns:
        str: Formatted currency string (e.g., "١٬١٥٠٫٠٠ ر.س")
    """
    # Format number with comma separators
    formatted = f"{float(amount):,.2f}"

    # Convert to Arabic numerals
    formatted_arabic = convert_to_arabic_numerals(formatted)

    # Replace decimal point and comma with Arabic equivalents
    formatted_arabic = formatted_arabic.replace('.', '٫')  # Arabic decimal separator
    formatted_arabic = formatted_arabic.replace(',', '٬')  # Arabic thousands separator

    return f"{formatted_arabic} ر.س"
