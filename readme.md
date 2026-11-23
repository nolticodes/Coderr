# Coderr

Coderr is a REST API for a platform where business users offer services and customers place orders.

It supports user authentication, profiles, offers with different service packages, orders, and reviews.

## Technologies

- Python
- Django
- Django REST Framework
- Token Authentication
- SQLite
- Git & GitHub

## Requirements

The following tools are required for local development:

- Git
- A Python 3 version compatible with the project dependencies
- pip

## Clone the Repository

```bash
git clone https://github.com/nolticodes/Coderr.git
cd Coderr
```

## Installation

### macOS / Linux

Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

### Windows

Create and activate a virtual environment in PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root, next to `manage.py`:

```dotenv
SECRET_KEY=your-django-secret-key
```

Replace the placeholder with your own Django secret key.

The `.env` file is required locally and must be excluded from version control.

## macOS / Linux: Database and Server

Apply database migrations:

```bash
python3 manage.py migrate
```

Optional: Create an administrator account:

```bash
python3 manage.py createsuperuser
```

Start the development server:

```bash
python3 manage.py runserver
```

## Windows: Database and Server

Apply database migrations:

```powershell
python manage.py migrate
```

Optional: Create an administrator account:

```powershell
python manage.py createsuperuser
```

Start the development server:

```powershell
python manage.py runserver
```

The development server is available at:

http://127.0.0.1:8000/

API endpoints use the `/api/` prefix.

## Authentication

Protected endpoints use Token Authentication.

Users can register with the account type `customer` or `business`. Successful registration or login returns an authentication token.

Include this token in the header of subsequent requests:

```http
Authorization: Token <your-token>
```

Example login request to `/api/login/`:

```json
{
  "username": "your-username",
  "password": "your-password"
}
```

## API Areas

| Area | Functionality |
| --- | --- |
| Authentication | Registration, login, and token-based access |
| Profiles | Retrieve profiles, update your own profile, and list customer or business profiles |
| Offers | List, filter, create, update, and delete offers |
| Offer Details | Retrieve individual service packages with prices, delivery times, revisions, and features |
| Orders | Order service packages, retrieve your orders, and update order statuses |
| Order Statistics | Count ongoing and completed orders for a business user |
| Reviews | List, filter, sort, create, update, and delete reviews |
| Base Information | Retrieve review counts, average ratings, business user counts, and offer counts |

### Offers

Offers contain three service packages. Package information includes:

- Title
- Price
- Delivery time
- Number of included revision rounds (`revisions`)
- Included services (`features`)
- Package type (`basic`, `standard`, or `premium`)

The offer list supports pagination and filtering by creator, minimum price, and maximum delivery time. Text search matches offer titles and descriptions.

### Orders

When an order is created, the selected package data is copied into the order as a snapshot.

This preserves the agreed prices and services if the original offer is changed later.

Available order statuses are:

- `in_progress`
- `completed`
- `cancelled`

### Permissions

Access rules depend on the endpoint:

- Business users can create offers.
- Only offer owners can update or delete their offers.
- Customers can create orders and reviews.
- Customers and providers can retrieve orders in which they participate.
- The business user assigned to an order can update its status.
- Staff users can delete orders.
- Only review authors can update or delete their reviews.

## Project Structure

The main features are organized into separate Django apps.

```text
Coderr/
├── auth_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   └── models.py
│
├── profile_app/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   └── models.py
│
├── offers_app/
│   ├── api/
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   └── models.py
│
├── orders_app/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   └── models.py
│
├── reviews_app/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── tests/
│   └── models.py
│
├── manage.py
├── requirements.txt
└── README.md
```

This overview shows the main feature apps. Project configuration and the app providing platform statistics are additional parts of the project.

## Tests

Tests are organized into separate `tests/` packages within the apps.

They cover:

- Registration and login
- Authentication and permissions
- Serializers and nested data
- Filtering and ordering
- Pagination
- API responses
- Order and platform statistics

Run all tests:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test offers_app
```

Run a specific test module:

```bash
python manage.py test auth_app.tests.test_registration
```

Run tests with detailed output:

```bash
python manage.py test --verbosity=2
```

On macOS / Linux, use `python3` if required.

Django uses a separate test database for database tests.

## Admin Interface

After creating a superuser, the Django admin interface is available at:

http://127.0.0.1:8000/admin/

Models registered in the respective `admin.py` files can be managed through this interface.