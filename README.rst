SmartShip API
=============

Python library to interact with the Posti SmartShip / Unifaun Online API.

TODO
----

* Docs
* Implement remaining attributes in Shipment as per schema
* Add logging where necessary

Compatibility
-------------

* Python 2.7+ or Python 3.4+

Usage
-----

Creating shipments
~~~~~~~~~~~~~~~~~~

This API supports the Smartship Shipments api for creating shipments and
then downloading the generated PDF's.

Carriers
''''''''

There are methods for certain carriers like Posti to cover more common use
cases. To create a shipment for the Posti carrier, for example:

.. code:: python

    from smartship.carriers.posti import create_shipment
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
    agent = {
        "quickId": "2",
    }
    shipment = create_shipment(
        "12345",  # Posti customer number
        "PO2102",  # Service ID
        receiver,
        sender,
        [{"copies": 1}],  # Parcels
        agent=agent,  # Optional pickup point
        pdf_config=pdf_config,  # Optional custom PDF config
     )

See more documentation in ``smartship.carriers.posti`` module.

PDF Config
''''''''''

If you want to pass a custom ``pdf_config``, it should have the following structure:

.. code:: python

    {
    "target1Media": "laser-a5",
    "target1YOffset": 0,
    "target1XOffset": 0
    }

With ``"target1Media"`` being one of the following options::

    "laser-a5"
    "laser-2a5"
    "laser-ste"
    "thermo-se"
    "thermo-225"

You can customize the offset with ``"target1YOffset"`` and ``"target1XOffset"`` parameters.

Client
~~~~~~

To send shipments and use other API resources, you need a client.
Initialize the client as follows with username and secret tokens.  Create
your API tokens in the `Unifaun Online portal
<https://www.unifaunonline.com/>`_.

.. code:: python

    from smartship import Client
    client = Client("username", "secret")

Sending shipments
'''''''''''''''''

Send a shipment as follows:

.. code:: python

    response = client.send_shipment(shipment)

Response will be a special ``ShipmentResponse`` wrapping a ``HttpResponse`` object with response code and
JSON content in ``response.data``.

Status codes:

* 201 - Shipment was created OK
* 422 - Validation error with the data. Raises a ``ShipmentResponseError``.

For errors see ``error.response.json()`` for details from Unifaun Online API.

Shipment address PDF slips
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have the response retrieve associated PDF data as follows:

.. code:: python

    data = response.get_pdfs(client)  # Client needed in case of additional fetching
    pdf_data = data[0][0]  # Simplest case with a single shipment with a single parcel

Agents
~~~~~~

Retrieve a list of agents (pickup points) as follows:

.. code:: python

    agents = client.get_agents("FI", "ITELLASP", "Iso Roobertinkatu 20-22", "00120")

Response will be an ``Agents`` object that can be iterated over for individual agent data.

Locations - NEW Posti Pickup Point API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NOTE: Old Posti Location Service API has been removed, as it is depreciated.

NOTE: nShift Agent service is paid, use of Posti Pickup Point is recommended.

Use of Posti Pickup Point -service requires (free) contract with Posti and then
requesting API credentials from them. As of 2025-10-01 there is no separate test API.

See:
- Documentation https://api.posti.fi/api-pickup-point.html
- OpenAPI Specification https://api.posti.fi/api-pickup-point-openapi.html
- Posti Developer Portal https://developer.posti.fi/ (Not yet included here.)


Authentication:
^^^^^^^^^^^^^^^

Import get_token from smartship.carriers.posti
``from smartship.carriers.posti import get_token``

It is highly recommended to cache token to avoid requesting new token every time you need to
do a query.

get_token parameters:
- API username (required)
- API password (required)
- API version, if not set defaults to oldest (and currently only) supported. Currently: "2025-04".

get_token returns:
- token: token used in authentication
- lifetime: token lifetime in seconds
- api_version: supported api_version. 
- url: specific url used based on API version requested.

``token, lifetime, url = get_token(username, password, posti_api_version)``

Get locations based on postal code or address:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``from smartship.carriers.posti import get_locations_by_address``

Parameters:
+-------------------------+------------------+----------+---------+
| **Parameter**           | **Default Value**|  **Comment**        |         |
+=========================+==================+==========+=========+
| access_token            |                  | Valid access token |         |
+-------------------------+------------------+----------+---------+
| posti_api_version       |                  | API version         |         |
+-------------------------+------------------+----------+---------+
| ppp_api_url             |                  | URL for API version         |         |
+-------------------------+------------------+----------+---------+
| language                | "fi"             | Result language: fi/sv/en         |         |
+-------------------------+------------------+----------+---------+
| country                 | "FI"             |          |         |
+-------------------------+------------------+----------+---------+
| city                    | None             |          |         |
+-------------------------+------------------+----------+---------+
| postcode                | None             |          |         |
+-------------------------+------------------+----------+---------+
| street_address          | None             |          |         |
+-------------------------+------------------+----------+---------+
| outdoor_locker          | None             | If set to False no outdoor lockers returned.         |         |
+-------------------------+------------------+----------+---------+
| wheelchair_accessibility| None             |          |         |
+-------------------------+------------------+----------+---------+
| open_on_weekends        | None             |          |         |
+-------------------------+------------------+----------+---------+
| adr_limited_quantities  | None             |          |         |
+-------------------------+------------------+----------+---------+
| saturday_delivery       | None             |          |         |
+-------------------------+------------------+----------+---------+
| box_only                | None             | Return only package lockers? If not set returns both.         |         |
+-------------------------+------------------+----------+---------+
| limit                   | 20               | How many results returned.         |         |
+-------------------------+------------------+----------+---------+

Example:
``get_locations_by_address(token, posti_api_version, url, postcode="00100", limit=1, language="en")``

Response will be a ``PickupPoints_<version>`` object that can be iterated over for individual location data.

Example result of the example query above:

.. code-block:: None
    PickupPoints_2025_04([
        {
            u'publicName': u'Posti, K-Market Etu-T\xf6\xf6l\xf6',
            u'routingServiceCode': u'3230',
            u'distanceInMeters': 292,
            u'capabilities': [
                {u'cutOffTime': None, u'name': u'accessibility', u'value': u'WHEELCHAIR'},
                {u'cutOffTime': None, u'name': u'expressDelivery', u'value': u'NOT_POSSIBLE'},
                {u'cutOffTime': None, u'name': u'identityCheck', u'value': u'NONE'},
                {u'cutOffTime': None, u'name': u'ADRLimitedQuantities', u'value': u'ALLOWED'},
                {u'cutOffTime': u'11:30:00', u'name': u'parcelDropoff', u'value': u'MANUAL_DROP'},
                {u'cutOffTime': None, u'name': u'parcelPickup', u'value': u'AVAILABLE'},
                {u'cutOffTime': u'11:30:00', u'name': u'parcelReturn', u'value': u'MANUAL_DROP'},
                {u'cutOffTime': None, u'name': u'saturdayDelivery', u'value': u'NOT_POSSIBLE'},
                {u'cutOffTime': None, u'name': u'sundayDelivery', u'value': u'NOT_POSSIBLE'}
            ],
            u'availability': {
                u'exceptions': [],
                u'openingHours': [
                    {u'dayOfWeek': u'MONDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'07:00:00', u'open24h': False},
                    {u'dayOfWeek': u'TUESDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'07:00:00', u'open24h': False},
                    {u'dayOfWeek': u'WEDNESDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'07:00:00', u'open24h': False},
                    {u'dayOfWeek': u'THURSDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'07:00:00', u'open24h': False},
                    {u'dayOfWeek': u'FRIDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'07:00:00', u'open24h': False},
                    {u'dayOfWeek': u'SATURDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'08:00:00', u'open24h': False},
                    {u'dayOfWeek': u'SUNDAY', u'closes': u'22:00:00', u'closed': False, u'opens': u'09:00:00', u'open24h': False}
                ]
            },
            u'location': {
                u'city': u'Helsinki',
                u'countryCode': u'FI',
                u'municipality': u'Helsinki',
                u'coordinates': {u'latitude': 60.17034, u'longitude': 24.92358},
                u'street': u'Lapuankatu 4',
                u'postcode': u'00100'
            },
            u'parcelLocker': False,
            u'careOf': u'c/o Posti, K-Market Etu-T\xf6\xf6l\xf6',
            u'id': u'001003230'
        }
    ])


Get location details if location ID (PupCode) is known:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also get Points details by requesting it by PupCode. (Point ID in new API.)

``get_location_by_pupcode(access_token, posti_api_version, ppp_api_url, 
            language="fi", pupcode=None, country="FI")``


Response will be a ``PickupPoints_<version>`` object that can be iterated over for individual location data.




Advanced usage
~~~~~~~~~~~~~~

See full Smartship `API documentation
<https://smartship.unifaun.com/rs-docs/>`_ for a full list of attributes
that shipments can be given.  All of these are supported when using
``smartship.shipments.Shipment`` directly.  Import the relevant objects
from ``smartship.objects`` and pass them to the ``Shipment`` object.

Development
-----------

Requirements
~~~~~~~~~~~~

Install the requirements to a virtual environment with::

    pip install -U setuptools pip  # These should be up to date
    pip install -r requirements-dev.txt

Tests
~~~~~

To test in the current virtual environment, run::

    py.test

To check the coding style, run::

    flake8

To test all supported environments, run::

    tox

Building documentation
~~~~~~~~~~~~~~~~~~~~~~

Build the documentation with::

    sphinx-build -b html docs docs/_build
