import os
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from models import User, UserCreateRequest
from database import Neo4JDatabase

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Neo4J database instance
db: Optional[Neo4JDatabase] = None

# Hardcoded users (fallback if database is not available)
HARDCODED_USERS = [
    User(
        id=1,
        email="john@example.com",
        firstName="John",
        lastName="Doe",
        roles=["ROLE_CUSTOMER"]
    ),
    User(
        id=2,
        email="jane@example.com",
        firstName="Jane",
        lastName="Smith",
        roles=["ROLE_SELLER"]
    ),
    User(
        id=3,
        email="bob@example.com",
        firstName="Bob",
        lastName="Johnson",
        roles=["ROLE_CUSTOMER", "ROLE_SELLER"]
    ),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global db
    
    # Startup
    neo4j_uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "")
    
    db = Neo4JDatabase(
        uri=neo4j_uri,
        username=neo4j_username,
        password=neo4j_password
    )
    
    # Try to connect to database
    if db.connect():
        logger.info("Neo4J database connected successfully")
        
        # Initialize database schema
        try:
            db.initialize_database()
            
            # Load hardcoded users into Neo4J if database is empty
            all_users = db.get_all_users()
            if not all_users:
                logger.info("Database is empty, loading hardcoded users...")
                for user in HARDCODED_USERS:
                    db.create_user(
                        user_id=user.id,
                        email=user.email,
                        first_name=user.firstName,
                        last_name=user.lastName,
                        roles=user.roles
                    )
                logger.info("Hardcoded users loaded into database")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    else:
        logger.warning("Could not connect to Neo4J database. Using hardcoded data.")
        db = None
    
    yield
    
    # Shutdown
    if db:
        db.disconnect()


# FastAPI app with lifespan
app = FastAPI(
    title="User Service",
    description="User microservice for mini-allegro",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if (db and db.is_connected()) else "disconnected"
    return {
        "status": "ok",
        "service": "user-service",
        "database": db_status
    }


@app.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def list_users():
    """List all users"""
    try:
        if db and db.is_connected():
            users_data = db.get_all_users()
            users = [User(**user) for user in users_data]
        else:
            users = HARDCODED_USERS
    except Exception as e:
        logger.error(f"Error fetching users from database: {e}")
        users = HARDCODED_USERS
    
    roles_histogram = {
        "ROLE_CUSTOMER": 0,
        "ROLE_SELLER": 0,
    }
    
    for user in users:
        for role in user.roles:
            if role in roles_histogram:
                roles_histogram[role] += 1
    
    logger.info(
        "Users fetched",
        extra={
            "endpoint": "/users",
            "results_count": len(users),
            "roles_histogram": roles_histogram,
        }
    )
    
    return users


@app.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(user_id: int):
    """Get a single user by ID"""
    try:
        if db and db.is_connected():
            user_data = db.get_user_by_id(user_id)
            if user_data:
                user = User(**user_data)
                logger.info(f"User {user_id} fetched from database")
                return user
        else:
            for user in HARDCODED_USERS:
                if user.id == user_id:
                    logger.info(f"User {user_id} fetched from hardcoded data")
                    return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        for user in HARDCODED_USERS:
            if user.id == user_id:
                return user
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_id} not found"
    )


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest):
    """Create a new user"""
    
    if not user_data.email or not user_data.firstName or not user_data.lastName:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email, firstName and lastName are required"
        )
    
    try:
        if db and db.is_connected():
            # Check if user with this email already exists
            if db.user_exists(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email {user_data.email} already exists"
                )
            
            # Find max ID
            all_users = db.get_all_users()
            max_id = max([u["id"] for u in all_users]) if all_users else 0
            new_id = max_id + 1
            
            # Create user
            created_user_data = db.create_user(
                user_id=new_id,
                email=user_data.email,
                first_name=user_data.firstName,
                last_name=user_data.lastName,
                roles=user_data.roles or ["ROLE_CUSTOMER"]
            )
            
            if created_user_data:
                logger.info(f"User created in database: {user_data.email}")
                return User(**created_user_data)
        else:
            # Fallback: create in hardcoded list
            max_id = max([u.id for u in HARDCODED_USERS]) if HARDCODED_USERS else 0
            new_user = User(
                id=max_id + 1,
                email=user_data.email,
                firstName=user_data.firstName,
                lastName=user_data.lastName,
                roles=user_data.roles or ["ROLE_CUSTOMER"]
            )
            logger.info(f"User created (hardcoded): {user_data.email}")
            return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@app.get("/users-super", response_model=List[dict], status_code=status.HTTP_200_OK)
async def list_super_users():
    """List users with super seller status"""
    try:
        if db and db.is_connected():
            users = db.get_users_with_super_seller()
        else:
            users = []
    except Exception as e:
        logger.error(f"Error fetching super users: {e}")
        users = []
    
    logger.info("Super users fetched", extra={"endpoint": "/users-super", "results_count": len(users)})
    return users


@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_data: UserCreateRequest):
    """Update an existing user"""
    try:
        if db and db.is_connected():
            # Check if user exists
            existing_user = db.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )

            # Update user
            updated_user_data = db.update_user(
                user_id=user_id,
                email=user_data.email,
                first_name=user_data.firstName,
                last_name=user_data.lastName,
                roles=user_data.roles or existing_user["roles"]
            )

            logger.info(f"User {user_id} updated in database")
            return User(**updated_user_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete an existing user"""
    try:
        if db and db.is_connected():
            # Check if user exists
            if not db.get_user_by_id(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )

            # Delete user
            db.delete_user(user_id)
            logger.info(f"User {user_id} deleted from database")
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
