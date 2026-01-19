import re
from bs4 import BeautifulSoup


def parse_costar_email(html_content):
    """Parse CoStar email HTML and extract property data."""
    soup = BeautifulSoup(html_content, 'lxml')
    properties = []
    current_search_name = None

    all_links = soup.find_all('a', href=True)

    for link in all_links:
        href = link.get('href', '')

        # Check for search name links
        if 'target=ViewAllAlerts' in href:
            search_text = link.get_text(strip=True)
            if search_text and 'View' not in search_text:
                current_search_name = search_text
            continue

        # Check for property links
        if 'target=PropertyAddress' in href and 'id=' in href:
            property_data = extract_property_from_link(link, href, current_search_name)
            if property_data and property_data.get('costar_id'):
                existing = next((p for p in properties if p['costar_id'] == property_data['costar_id']), None)
                if existing:
                    for key, value in property_data.items():
                        if value and not existing.get(key):
                            existing[key] = value
                else:
                    properties.append(property_data)

    return properties


def extract_property_from_link(link, href, search_name):
    """Extract property data from a link element."""
    property_data = {
        'costar_id': None, 'address': None, 'city': None,
        'state': None, 'zip_code': None, 'property_type': None,
        'square_feet': None, 'year_built': None, 'price': None,
        'price_per_sf': None, 'cap_rate': None, 'image_url': None,
        'costar_url': href, 'search_name': search_name
    }

    costar_id = extract_id_from_url(href)
    if costar_id:
        property_data['costar_id'] = costar_id

    link_text = link.get_text(strip=True)

    if link_text and not link_text.startswith('http'):
        if is_address(link_text):
            property_data['address'] = link_text
        elif is_city_state_zip(link_text):
            parsed = parse_city_state_zip(link_text)
            property_data.update(parsed)

    img = link.find('img')
    if img and img.get('src'):
        property_data['image_url'] = img.get('src')

    parent = link.find_parent('table') or link.find_parent('td')
    if parent:
        property_data = extract_property_details(parent, property_data)

    return property_data


def extract_id_from_url(url):
    match = re.search(r'[&?]id=(\d+)', url)
    return match.group(1) if match else None


def is_address(text):
    return bool(re.match(r'^\d+\s+\w+', text))


def is_city_state_zip(text):
    return bool(re.search(r'[A-Z]{2}\s+\d{5}', text))


def parse_city_state_zip(text):
    result = {'city': None, 'state': None, 'zip_code': None, 'property_type': None}
    parts = re.split(r'\s*[･·]\s*', text)
    location_part = parts[0].strip()

    if len(parts) > 1:
        result['property_type'] = parts[1].strip()

    match = re.match(r'^(.+?),\s*([A-Z]{2})\s*(\d{5})?', location_part)
    if match:
        result['city'] = match.group(1).strip()
        result['state'] = match.group(2)
        result['zip_code'] = match.group(3) if match.group(3) else None

    return result


def extract_property_details(container, property_data):
    text = container.get_text(' ', strip=True)

    sf_match = re.search(r'([\d,]+)\s*SF', text)
    if sf_match:
        property_data['square_feet'] = sf_match.group(1).replace(',', '')

    ac_match = re.search(r'([\d.]+)\s*AC', text)
    if ac_match and not property_data.get('square_feet'):
        property_data['square_feet'] = f"{ac_match.group(1)} AC"

    year_match = re.search(r'Built\s+(\d{4})', text)
    if year_match:
        property_data['year_built'] = year_match.group(1)

    price_match = re.search(r'For Sale:\s*([\$\d,]+|Price Not Disclosed)', text)
    if price_match:
        property_data['price'] = price_match.group(1)

    psf_match = re.search(r'\(([\$\d,.]+)/SF\)', text)
    if psf_match:
        property_data['price_per_sf'] = psf_match.group(1)

    cap_match = re.search(r'([\d.]+)%\s*Cap\s*Rate', text)
    if cap_match:
        property_data['cap_rate'] = f"{cap_match.group(1)}%"

    if not property_data.get('property_type'):
        types = ['Retail', 'Office', 'Industrial', 'Warehouse', 'Fast Food', 
                 'Drug Store', 'Flex', 'Commercial Land', 'Vacant Land']
        for ptype in types:
            if ptype in text:
                property_data['property_type'] = ptype
                break

    return property_data
