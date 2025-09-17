# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy

import requests

from ..objects import (
    Agent, PickupPoints_2025_04, Parcels, PDFConfig, Receiver, Sender, SenderPartners,
    Service)
from ..shipments import Shipment

import base64

CARRIER_CODE = "POSTI"
CARRIER_DESCRIPTION = "Posti Oy, Paketit ja kuljetusyksiköt"

SERVICES = {
    "IT14I": "Posti - Express Business Day parcel (Ulkomaa)",
    "ITKY14I": "Posti - Express Business Day pallet (Ulkomaa)",
    "ITPR": "Posti - Priority Parcel",
    "PO2017": "Posti - EMS",
    "PO2017D": "Posti - EMS DocPack",
    "PO2102": "Posti - Express-paketti",
    "PO2103": "Posti - Postipaketti",
    "PO2104": "Posti - Kotipaketti",
    "PO2108": "Posti - Palautus",
    "PO2114": "Posti - Ruokakuljetus",
    "PO2115": "Posti - Ruokakuljetus automaattiin",
    "PO2144": "Posti - Express-rahti",
    "PO2331": "Posti - Postal Parcel Baltics",
    "PO2338": "Posti - Postal Parcel Baltics Return",
    "PO2461": "Posti - Pikkupaketti",
    "PO2711": "Posti - Parcel Connect",
    "PO2718": "Posti - Parcel Return Connect",
    "PO5001": "Posti - Pikakirje",
    "PO5002": "Posti - Economy-kirje postiennakolla",
    "PO5003": "Posti - Kirjattu kirje",
    "PO5004": "Posti - Saantitodistuskirje",
    "PO5006": "Posti - Postivakuutettu",
    "PO5007": "Posti - Priority-kirje postiennakolla",
}

NATIONAL_SERVICE_KEYS = [
    "ITPR",
    "PO2102",
    "PO2103",
    "PO2104",
    "PO2108",
    "PO2114",
    "PO2115",
    "PO2144",
    "PO2461",
    "PO5001",
    "PO5002",
    "PO5003",
    "PO5004",
    "PO5006",
    "PO5007",
]

NATIONAL_SERVICES = {
    key: description
    for (key, description) in SERVICES.items()
    if key in NATIONAL_SERVICE_KEYS
}

ADDITIONAL_SERVICES = {
    "COD": "Postiennakko",
    "COLD": "Jääkaappilämpö",
    "DLV": "Kotiinkuljetus",
    "DLV00": "Samana päivänä 00",
    "DLV09": "Aamuksi 09",
    "DLV21": "Illaksi 21",
    "DLVCALL": "Soitto ennen jakelua",
    "DLVANOT": "Jakeluajankohdan sopiminen puhelimitse",
    "DLVDEP": "Toimitus terminaaliin",
    "DLVINST": "Käyttökuntoon asennus",
    "DLVNOPOD": "Luovuttaminen ilman vastaanottajan kuittausta",
    "DLVPRIV": "Jakelu yksityishenkilölle",
    "DLVSAT": "Lauantaijakelu",
    "DLVT": "Aikataulutettu jakelu",
    "DNG": "Vaarallisten aineiden kuljetus (VAK) / LQ Kuljetus",
    "FDNGPP": "LQ Prosessilupa",
    "FRAG": "Särkyvä",
    "FRZ": "Pakaste",
    "INSU": "Kuljetusvakuutus",
    "MAXI": "Maksikoko",
    "MPRC": "Monikollilähetys",
    "NOBOX": "Ohjauksen esto ulkoautomaattiin",
    "NOT": "Sähköinen saapumisilmoitus",
    "NOTLTR": "Saapumisilmoitus kirjeenä",
    "OPAY": "Maksaja muu kuin lähettäjä",
    "PERS": "Henkilökohtaisesti luovutettava",
    "PRENOT": "Sähköinen ennakkoilmoitus",
    "PUPDEP": "Nouto terminaalista",
    "PUPOPT": "Vaihtoehtoinen noutopiste",
    "RBLOCK": "Pakettiohjauksen esto",
    "RECYCLE": "Kuljetus kierrätykseen",
    "REG": "Kirjaaminen",
    "REMIPOST": "Noutomuistutus kirjeenä",
    "RETNEXT": "Säilytysajan pidennys",
    "SPTR": "Suri",
    "TECH": "Nosturipalvelu",
    "WARM": "Lämminkuljetus",
}

VALID_ADDITIONAL_SERVICES = {
    'IT14I': ['COD', 'DLV', 'DLVCALL', 'DLVNOPOD', 'FDNGPP', 'FRAG', 'MPRC', 'OPAY', 'SPTR'],
    'ITKY14I': [
        'COD', 'DLV00', 'DLV09', 'DLV21', 'DLVCALL', 'DLVINST', 'DLVNOPOD', 'DNG', 'MPRC',
        'OPAY', 'PERS', 'PRENOT', 'PUPDEP', 'RECYCLE', 'SPTR'],
    'ITPR': ['OPAY'],
    'PO2017': ['OPAY'],
    'PO2017D': ['OPAY'],
    'PO2102': [
        'COD', 'DLV00', 'DLV09', 'DLVCALL', 'DLVINST', 'DLVNOPOD', 'DLVSAT', 'DNG',
        'FDNGPP', 'FRAG', 'NOT', 'OPAY', 'PERS', 'PRENOT', 'RBLOCK', 'RECYCLE', 'SPTR'
    ],
    'PO2103': [
        'COD', 'FDNGPP', 'FRAG', 'NOBOX', 'NOT', 'NOTLTR', 'OPAY', 'PERS', 'PUPOPT',
        'RBLOCK', 'REG', 'REMIPOST', 'RETNEXT', 'SPTR'],
    'PO2104': ['COD', 'DLVNOPOD', 'DLVANOT', 'DNG', 'FDNGPP', 'FRAG', 'OPAY', 'PERS', 'SPTR'],
    'PO2108': ['FDNGPP', 'FRAG', 'OPAY', 'SPTR'],
    'PO2114': ['COLD', 'OPAY', 'FDNGPP', 'FRZ'],
    'PO2115': ['COLD', 'OPAY', 'FDNGPP', 'FRZ'],
    'PO2144': [
        'COD', 'DLV00', 'DLV09', 'DLV21', 'DLVANOT', 'DLVCALL', 'DLVINST', 'DLVNOPOD', 'DNG',
        'OPAY', 'PERS', 'PRENOT', 'RECYCLE', 'WARM'
    ],
    'PO2331': ['FDNGPP', 'OPAY', 'SPTR', 'FRAG', 'NOT'],
    'PO2338': ['FDNGPP', 'OPAY', 'SPTR', 'FRAG'],
    'PO2461': ['OPAY'],
    'PO2711': ['COD', 'DLV', 'OPAY', 'PUPOPT', 'SPTR'],
    'PO2718': ['OPAY', 'SPTR'],
    'PO5001': ['DLVSAT', 'OPAY'],
    'PO5002': ['COD', 'NOT', 'OPAY', 'REMIPOST'],
    'PO5003': ['NOT', 'OPAY', 'PERS', 'REMIPOST'],
    'PO5004': ['NOT', 'OPAY', 'PERS', 'REMIPOST'],
    'PO5006': ['COD', 'INSU', 'NOT', 'OPAY', 'PERS', 'REMIPOST'],
    'PO5007': ['COD', 'NOT', 'OPAY', 'REMIPOST'],
}

POSTI_PICKUP_POINT_DEFAULT_API_VERSION = "2025-04"

POSTI_PICKUP_POINT_API_AUTH = "https://gateway-auth.posti.fi/api/v1/token"


class MobileReceiver(Receiver):
    schema = deepcopy(Receiver.schema)
    schema["oneOf"][0] = {"required": ["name", "city", "country", "mobile"]}


class WeightedParcels(Parcels):
    schema = deepcopy(Parcels.schema)
    schema["items"]["required"].append("weight")


def create_shipment(
        custno, service_id, receiver, sender, parcels,
        agent=None, order_no=None, sender_reference=None, pdf_config=None, addons=None, free_text=None,):
    """
    Create a shipment using the Posti carrier.

    Example simplest case usage:
        receiver = {
            "name": "Anders Innovations",
            "city": "Helsinki",
            "country": "FI",
            "address1": "Iso Roobertinkatu 20-22",
            "zipcode": "00120"
        }
        sender = {
            "quickId": "1",
        }
        shipment = create_shipment("12345", "PO2102", receiver, sender, [{"copies": 1}])

    :param custno: Posti customer number.
    :type custno: str
    :param service_id: Service to use, see `SERVICES` constant or API documentation.
    :type service_id: str
    :param receiver: Receiver of the shipment. Must either have a 'quickId' or enough address information.
        See example receiver data above. Required receiver information can depend on service chosen. If necessary,
        check service lists in Unifaun Online and API docs at https://smartship.unifaun.com/rs-docs/##creating_shipments
    :type receiver: dict
    :param parcels: Parcels to send in this shipment. This needs to be a list of items, with at minimum the amount
        of items in the parcel. For example, a shipment with one item:
            [
                {
                    "copies": 1,
                },
            ]
        See full specification of in the Smartship API documentation at
        https://smartship.unifaun.com/rs-docs/##creating_shipments
    :type parcels: list
    :param sender: Sender information. Must either have a 'quickId' or enough address information.
    :type sender: dict
    :param agent: Pickup agent (optional)
    :type agent: dict
    :param order_no: Order number (optional)
    :type order_no: str
    :param sender_reference: Sender reference (optional)
    :type sender_reference: str
    :param pdf_config: PDF config (optional)
    :type pdf_config: dict
    :param addons: Service addons. Available addons depend on chosen service (optional). See Unfifaun Online
        service lists. Defined as a list of dictionaries containing addon 'id' and additional information, for example:
            [
                {
                    "id": "DNG",
                    "declarant": "Firma Oy",
                },
                {
                    "id": "SPTR",
                },
            ]
    :type addons: list
    :param free_text: free text (optional)
    :type free_text: str
    :return: Shipment instance
    :rtype: smartship.shipments.Shipment
    """
    _validate_create_shipment(service_id)
    receiver_class = _infer_receiver_class(service_id, agent)
    parcels_class = _infer_parcels_class(service_id)

    kwargs = {
        "sender": Sender(sender),
        "senderPartners": SenderPartners([{"id": CARRIER_CODE, "custNo": custno}]),
        "receiver": receiver_class(receiver),
        "parcels": parcels_class(parcels),
        "service": _build_service(addons, service_id),
    }
    if agent:
        kwargs["agent"] = Agent(agent)
    if order_no:
        kwargs["orderNo"] = order_no
    if sender_reference:
        kwargs["senderReference"] = sender_reference
    if pdf_config:
        kwargs["pdfConfig"] = PDFConfig(pdf_config)
    if free_text:
        kwargs["freeText1"] = free_text
    return Shipment(**kwargs)


def _build_service(addons, service_id):
    service = Service({"id": service_id})
    if addons:
        service["addons"] = addons
    return service


def _validate_create_shipment(service_id):
    if service_id not in SERVICES:
        raise ValueError("Invalid 'service_id'.")


def _infer_receiver_class(service_id, agent):
    if service_id == "PO2104":
        return MobileReceiver
    if service_id == "PO2103" and agent:
        return MobileReceiver
    return Receiver


def _infer_parcels_class(service_id):
    if service_id == "PO5041":
        return WeightedParcels
    return Parcels

def get_token(username, password, posti_api_version=POSTI_PICKUP_POINT_DEFAULT_API_VERSION):

    url = POSTI_PICKUP_POINT_API_AUTH

    response = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": username,
            "client_secret": password
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        })

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        token_lifetime = response.json().get("expires_in")
        api_version_details = response.json().get('posti_fi', {}).get('targets', {}).get(posti_api_version, {})
        if not api_version_details:
            print("Requested PPP API version not compatible with authenticated response.")
            return None
        else:
            ppp_api_url = api_version_details.get('url')

    else:
        print("Failed to obtain the OAuth token:", response.status_code)
        print(response)
        return None

    return access_token, token_lifetime, ppp_api_url

def get_location_by_pupcode_2025_04(access_token, ppp_api_url, 
            language, pupCode, country):

    url = "{}/pickuppoints/{}/{}".format(ppp_api_url, country, pupCode)

    header = {
        "Accept-Language":language,
        "Authorization": "Bearer {}".format(access_token)
    }

    response = requests.get(url, headers=header)
    print(response.json())

    points = response.json().get("pickupPoints")
    if points:
        return PickupPoints_2025_04(points)
    else:
        return None

def get_location_by_pupcode(access_token, posti_api_version, ppp_api_url, 
            language="fi", pupCode=None, country="FI"):
    if posti_api_version == "2025-04":
        return get_location_by_pupcode_2025_04(access_token, ppp_api_url, 
            language, pupCode, country)

def get_locations_by_address_2025_04(access_token, ppp_api_url,
            language, country, city, postcode, street_address, limit, filters, box_only):
   
    url = "{}/pickuppoints".format(ppp_api_url)

    header = {
        "Accept-Language": language,
        "Authorization": "Bearer {}".format(access_token)
    }

    params = {
        "searchCriteria":{
            "location": {
                "countryCode": country,
                "postcode": postcode,
            },
            "serviceFilters": filters
        },
        "limit": limit
    }
    if street_address:
        params["searchCriteria"]["location"]["street"] = street_address

    if city:
        params["searchCriteria"]["location"]["city"] = city
    
    if box_only is not None:
        params["searchCriteria"]["parcelLocker"] = box_only
    
    response = requests.post(url, headers=header, json=params)
    print(response)
    print(response.status_code)
    print(response.json())

    points = response.json().get("pickupPoints")
    if points:
        return PickupPoints_2025_04(points)
    else:
        return None 

def get_locations_by_address(access_token, posti_api_version, ppp_api_url, 
            language="fi", country="FI", city=None, postcode=None,
            street_address=None, limit=20, filters=None, box_only=None):
    if posti_api_version == "2025-04":
        return get_locations_by_address_2025_04(access_token, ppp_api_url,
            language, country, city, postcode, street_address, limit, filters, box_only)


def get_additional_services(service_id):
    if service_id not in VALID_ADDITIONAL_SERVICES:
        return {}
    result = {}
    for service_code in VALID_ADDITIONAL_SERVICES[service_id]:
        result[service_code] = ADDITIONAL_SERVICES[service_code]
    return result
