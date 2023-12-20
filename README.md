# Appointment Scheduling System

This project is an appointment scheduling system where clients can book available slots provided by service providers. It features a RESTful API for managing clients, providers, available slots, and appointments.

## Setup and Installation

1. **Build and Run Docker Containers:**
   ```
   docker-compose up --build
   ```
   This command builds the Docker image for the Django application and starts the containers defined in the `docker-compose.yml` file.

2. **Migrate the Database:**
   ```
   docker-compose exec web python manage.py migrate
   ```
   This command applies database migrations.

3. **Create a Superuser (Optional):**
   ```
   docker-compose exec web python manage.py createsuperuser
   ```
   Follow the prompts to create a superuser account for accessing the Django admin panel.

## API Endpoints

### Clients

- **Create a Client:**
  `POST /clients/`
  ```json
  {
    "user": <user_id>
  }
  ```

- **List Clients:**
  `GET /clients/`

- **Retrieve, Update, Delete a Client:**
  `GET, PUT, DELETE /clients/<id>/`

### Providers

- **Create a Provider:**
  `POST /providers/`
  ```json
  {
    "user": <user_id>
  }
  ```

- **List Providers:**
  `GET /providers/`

- **Retrieve, Update, Delete a Provider:**
  `GET, PUT, DELETE /providers/<id>/`

### Available Slots

- **Create Slots:**
  `POST /available_slots/`
  ```json
  {
    "provider": <provider_id>,
    "start_time": "YYYY-MM-DDTHH:MM:SS",
    "end_time": "YYYY-MM-DDTHH:MM:SS"
  }
  ```

- **List Slots:**
  `GET /available_slots/`
  - Query Parameters: `provider`, `date` (YYYY-MM-DD)

### Appointment Reservations

- **Create a Reservation:**
  `POST /appointment_reservations/`
  ```json
  {
    "client": <client_id>,
    "slot": <slot_id>
  }
  ```

- **List Reservations:**
  `GET /appointment_reservations/`

- **Retrieve, Update, Delete a Reservation:**
  `GET, PUT, DELETE /appointment_reservations/<id>/`

- **Confirm a Reservation:**
  `POST /appointment_reservations/<id>/confirm/`

## Notes

- Ensure all datetime values are in ISO 8601 format and timezone-aware.
- Replace `<id>`, `<user_id>`, `<provider_id>`, `<client_id>`, and `<slot_id>` with actual numeric IDs.
