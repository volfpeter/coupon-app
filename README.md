# Coupon management example application

## Notes

A company offers various paid services to its customers and occasionally they want to issue coupons. This is a super-simple coupon management application that solves this using FastAPI and an SQL backend.

There are (at least) two types of coupons:

- fixed sum,
- percentage-based.

Q: Does fixed sum coupons need a currency?
A: Probably not, we can convert on the UI if needed, although in that case we could end up with ugly, fractional numbers.

The application should provide a REST API for:

- creating coupons,
- checking coupon validity,
- activting/using coupon,
- disabling coupons.

A coupon could belong to a single customer, or it can be used by anyone who has the coupone code.

## Schema

Customer:

- id (primary key)
- name (str)
- created_at (date, auto)

Coupon:

- id (primary key)
- created_at (date, auto)
- code (unique str)
- description (str)
- discount (float)
- discount_type (enum)
- customer (optional, foreign key)
- valid_from (date)
- valid_until (date)

Note: having `customer` in `Coupon` means a coupon can be used either by a single customer or by anyone. Supporting "group" coupon would require an additional link table (and the removal of the `customer` attribute).

## Testing

TODO

## Development

Dependencies: `fastapi[all] sqlmodel typer[all]`.

Linting and formatting: `black mypy ruff`.

Testing: `pytest`.

## Dependency management

Currently `pipenv`, probably moving to `poetry` in the future.
