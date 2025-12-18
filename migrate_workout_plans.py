from sqlalchemy import inspect, text
from database import engine


def ensure_workout_plans_table(connection):
    inspector = inspect(connection)
    if inspector.has_table("workout_plans"):
        return

    dialect = engine.dialect.name
    if dialect == "postgresql":
        connection.execute(
            text(
                """
                CREATE TABLE workout_plans (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT timezone('utc', now()),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT timezone('utc', now())
                )
                """
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_workout_plans_name ON workout_plans (name)")
        )
    elif dialect == "sqlite":
        connection.execute(
            text(
                """
                CREATE TABLE workout_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_workout_plans_name ON workout_plans (name)")
        )
    else:
        raise RuntimeError(f"Unsupported dialect: {dialect}")


def ensure_workouts_plan_column(connection):
    inspector = inspect(connection)
    columns = {column["name"] for column in inspector.get_columns("workouts")}
    dialect = engine.dialect.name

    if "plan_id" not in columns:
        if dialect == "postgresql":
            connection.execute(text("ALTER TABLE workouts ADD COLUMN IF NOT EXISTS plan_id INTEGER"))
        elif dialect == "sqlite":
            connection.execute(text("ALTER TABLE workouts ADD COLUMN plan_id INTEGER"))
        else:
            raise RuntimeError(f"Unsupported dialect: {dialect}")

    if dialect == "postgresql":
        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'workouts_plan_id_fkey'
                    ) THEN
                        ALTER TABLE workouts
                        ADD CONSTRAINT workouts_plan_id_fkey
                        FOREIGN KEY (plan_id)
                        REFERENCES workout_plans(id)
                        ON DELETE SET NULL;
                    END IF;
                END;
                $$;
                """
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_workouts_plan_id ON workouts (plan_id)")
        )


def main():
    with engine.begin() as connection:
        ensure_workout_plans_table(connection)
        ensure_workouts_plan_column(connection)


if __name__ == "__main__":
    main()
    print("Workout plan migration applied.")
