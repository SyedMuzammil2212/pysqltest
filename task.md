Backend Assessment: Simple E-commerce API

Create a branch from main - "yourname" and "yourname/task"
Code the entire app in "yourname/task"
And after you are done with your task raise a PR from "yourname/task" to "yourname" not main

Build a backend using FastAPI, PostgreSQL, SQLAlchemy or raw SQL, and JWT authentication.

There is one user type: registered users. Users can manage the shared product catalog, maintain their own carts, place orders, and view bills. No frontend or product images are required.

## 1. Required APIs

Prefix every route with `/api/v1`.

### Authentication (2)

- `POST /auth/register`: Register a user.
- `POST /auth/login`: Return a JWT access token.

### Profile (3)

- `GET /users/me`: View your profile.
- `PATCH /users/me`: Update your name and phone.
- `PATCH /users/me/password`: Change your password after verifying your current password.

### Addresses (5)

- `POST /addresses`: Add an address.
- `GET /addresses`: List your addresses.
- `GET /addresses/{id}`: View your address.
- `PATCH /addresses/{id}`: Update your address.
- `DELETE /addresses/{id}`: Delete your address.

### Categories (5)

- `POST /categories`: Create a category.
- `GET /categories`: List categories.
- `GET /categories/{id}`: View a category.
- `PATCH /categories/{id}`: Update a category.
- `DELETE /categories/{id}`: Delete an empty category.

### Products (7)

- `POST /products`: Create a product with a category_id.
- `GET /products`: List and search active products.
- `GET /products/{id}`: View an active product.
- `PATCH /products/{id}`: Update a product, including its category_id.
- `PATCH /products/{id}/stock`: Update available stock.
- `DELETE /products/{id}`: Deactivate a product.
- `GET /categories/{id}/products`: List active products in a category.

### Cart (5)

- `GET /cart`: View your cart and its total.
- `POST /cart/items`: Add a product to your cart.
- `PATCH /cart/items/{id}`: Update an item's quantity.
- `DELETE /cart/items/{id}`: Remove an item.
- `DELETE /cart`: Clear your cart.

### Orders (4)

- `POST /orders`: Place an order using your cart and saved address.
- `GET /orders`: List your orders.
- `GET /orders/{id}`: View your order.
- `POST /orders/{id}/cancel`: Cancel your pending order.

### Bills (2)

- `GET /orders/{id}/bill`: View your order's bill.
- `GET /bills`: List your bills.

**Total: 33 APIs.**

Product and category browsing is public. All other operations require login. Any authenticated user can create, update, or deactivate products and manage categories for this assessment.

## 2. Database Tables

- `users`: id, name, email, password_hash, phone, created_at.
- `addresses`: id, user_id, address_line_1, address_line_2, city, state, postal_code.
- `categories`: id, name, description.
- `products`: id, category_id, sku, name, description, price, stock, is_active.
- `carts`: id, user_id.
- `cart_items`: id, cart_id, product_id, quantity.
- `orders`: id, user_id, shipping_address_snapshot, status, total, created_at.
- `order_items`: id, order_id, product_id, product_name_snapshot, quantity, unit_price, subtotal.
- `bills`: id, user_id, order_id, bill_number, subtotal, delivery_fee, final_total, created_at.

Use primary keys and foreign keys for all relationships. In particular:

- `products.category_id` references `categories.id`.
- `orders.user_id` references `users.id`.
- `bills.user_id` references `users.id`.
- `bills.order_id` references `orders.id`.

Each product belongs to one category. Each order has one bill, created in the same transaction. Make bills.order_id unique to prevent duplicate bills. The bill and its order must belong to the same user.

Make user emails, category names, product SKUs, and bill numbers unique. Allow one cart per user and one cart item per product per cart. Store money using decimal fields.

## 3. Business Rules

- Hash passwords and return a JWT access token after successful login.
- Users can access only their own profile, addresses, cart, orders, and bills.
- Set orders.user_id from the authenticated JWT user. Do not accept it from the request body.
- Set bills.user_id from the order's user_id. Do not accept it from the request body.
- Filter order and bill listings by the logged-in user's ID, and verify ownership when retrieving an individual record.
- Validate that category_id exists when creating a product or changing its category.
- Product prices must be positive. Stock cannot be negative. Quantities must be positive whole numbers.
- Adding the same product to a cart increases its quantity.
- Product listing supports name search, category filtering, pagination, and price sorting.
- Deactivating a product removes it from public listings and prevents new orders for it.
- Delete a category only when no products, including inactive products, reference it.

## 4. Order Placement

When a user places an order:

1. Require a nonempty cart and one of the user's saved addresses.
2. Check product availability and stock.
3. Calculate totals using prices from the database.
4. Create the order and bill, reduce stock, and clear the cart in one database transaction. Prevent stock from becoming negative if two users order at the same time.
5. Send a confirmation email after the order is saved.

Preserve product names, prices, and the shipping address in the order so later edits do not change its details.

Use cash on delivery. Orders have two statuses: pending and cancelled. Users can cancel their own pending orders. Cancellation restores stock exactly once, in the same transaction as the status change.

## 5. Billing and Email

Return bills as JSON, including user_id and order_id.

**Final total = sum of item subtotals + fixed delivery fee.**

Send an order-confirmation email containing the order number, items, quantities, total, and shipping address. Use FastAPI background tasks and configurable SMTP settings. Email failure must not undo the order.

## 6. Deliverables

- Backend source code.
- Database migrations and sample categories and products.
- .env.example with database, JWT, delivery-fee, and SMTP settings.
- README with setup and run instructions.
- Swagger documentation for all APIs.
- Tests for login, data ownership, valid category relationships, cart updates, order placement, insufficient stock, cancellation, and correct order/bill user IDs.

Copy .env.example to .env and replace placeholder values before running. Keep .env out of version control. The example database URL is for SQLAlchemy; if using raw SQL, use the connection format required by your PostgreSQL driver. The SMTP example assumes a local test mail server on port 1025.