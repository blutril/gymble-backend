# Gymble Backend API

A FastAPI-based REST API for a gym workout tracking application.

## Features

- **User Management**: Create and manage user accounts
- **Exercise Library**: Pre-populated database with common exercises
- **Workout Creation**: Build custom workout routines with multiple exercises
- **Workout Sessions**: Track workout sessions with sets, reps, and weights
- **Progress Tracking**: Monitor workout history and performance

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Production-ready relational database (with Docker)
- **Pydantic**: Data validation using Python type annotations
- **Passlib**: Password hashing
- **Docker**: Containerized PostgreSQL database

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Docker and Docker Compose (for PostgreSQL database)

### Installation

1. **Navigate to the backend directory**:
   ```bash
   cd gymble-backend
   ```

2. **Start PostgreSQL with Docker**:
   ```bash
   docker-compose up -d
   ```
   
   This will start a PostgreSQL container on port 5432.

3. **Create environment configuration**:
   ```bash
   cp .env.example .env
   ```
   
   The default configuration connects to the Docker PostgreSQL instance.

4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

5. **Activate the virtual environment**:
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

6. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

7. **Seed the database with exercises** (optional but recommended):
   ```bash
   python seed_exercises.py
   ```

### Running the Server

Start the development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /api/users/` - Create a new user
- `GET /api/users/` - Get all users
- `GET /api/users/{user_id}` - Get specific user

### Exercises
- `POST /api/exercises/` - Create an exercise
- `GET /api/exercises/` - Get all exercises (supports filtering)
- `GET /api/exercises/{exercise_id}` - Get specific exercise
- `PUT /api/exercises/{exercise_id}` - Update an exercise
- `DELETE /api/exercises/{exercise_id}` - Delete an exercise

### Workouts
- `POST /api/workouts/?user_id={user_id}` - Create a workout
- `GET /api/workouts/?user_id={user_id}` - Get user's workouts
- `GET /api/workouts/{workout_id}` - Get specific workout
- `PUT /api/workouts/{workout_id}` - Update a workout
- `DELETE /api/workouts/{workout_id}` - Delete a workout

### Workout Sessions
- `POST /api/sessions/?user_id={user_id}` - Start a workout session
- `GET /api/sessions/?user_id={user_id}` - Get user's sessions
- `GET /api/sessions/{session_id}` - Get specific session
- `PUT /api/sessions/{session_id}` - Update a session
- `POST /api/sessions/{session_id}/complete` - Complete a session
- `DELETE /api/sessions/{session_id}` - Delete a session

## Database Models

### User
- id, username, email, full_name, hashed_password, created_at

### Exercise
- id, name, description, muscle_group, equipment, difficulty, instructions

### Workout
- id, user_id, name, description, created_at, updated_at

### WorkoutExercise
- id, workout_id, exercise_id, sets, reps, rest_seconds, order

### WorkoutSession
- id, user_id, workout_id, started_at, completed_at, duration_minutes, notes

### SessionExercise
- id, session_id, exercise_id, sets_completed, reps_completed, weight, notes

## Database Management

### Using PostgreSQL (Recommended)

The project includes Docker Compose for easy PostgreSQL setup:

```bash
# Start the database
docker-compose up -d

# Stop the database
docker-compose down

# View database logs
docker-compose logs -f postgres

# Reset database (removes all data)
docker-compose down -v
docker-compose up -d
```

### Environment Variables

The `.env` file configures the database connection:

**PostgreSQL (default)**:
```
DATABASE_URL=postgresql://gymble:gymble_password@localhost:5432/gymble
```

**SQLite (alternative for development)**:
```
DATABASE_URL=sqlite:///./gymble.db
```

### Database Credentials

Default PostgreSQL credentials (defined in `docker-compose.yml`):
- **Username**: gymble
- **Password**: gymble_password
- **Database**: gymble
- **Host**: localhost
- **Port**: 5432

**Note**: Change these credentials for production deployments!

## Development

The API uses hot-reloading in development mode. Any changes to the code will automatically restart the server.

### Quick Start Commands

```bash
# Start database
docker-compose up -d

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## CORS

Currently configured to allow all origins for development. Update the `allow_origins` in `main.py` for production use.

## Troubleshooting

### Database Connection Issues

**Error**: "could not connect to server"
- Ensure Docker is running: `docker ps`
- Check PostgreSQL container status: `docker-compose ps`
- Restart the container: `docker-compose restart`

**Error**: "password authentication failed"
- Verify credentials in `.env` match those in `docker-compose.yml`
- Try resetting the database: `docker-compose down -v && docker-compose up -d`

### Migration Issues

If you need to reset the database:
```bash
docker-compose down -v  # Removes database volume
docker-compose up -d    # Creates fresh database
python seed_exercises.py  # Re-seed data
```
