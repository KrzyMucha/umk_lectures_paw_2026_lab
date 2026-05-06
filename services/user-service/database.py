"""Neo4J database connection and utilities"""
import os
import logging
from typing import Optional

from neo4j import GraphDatabase, Session, Driver
from neo4j.exceptions import ServiceUnavailable, DriverError

logger = logging.getLogger(__name__)


class Neo4JDatabase:
    """Neo4J database manager"""

    def __init__(self, uri: str, username: str = "neo4j", password: str = ""):
        """Initialize Neo4J database connection"""
        self.uri = uri or os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")

        self._driver: Optional[Driver] = None
        self._connected = False

    def connect(self) -> bool:
        """Establish connection to Neo4J"""
        try:
            logger.info(f"Connecting to Neo4J at {self.uri}...")
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                encrypted=False,
                trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
            )

            # Test connection
            with self._driver.session() as session:
                result = session.run("RETURN 1")
                result.single()

            self._connected = True
            logger.info("Successfully connected to Neo4J")
            return True

        except (ServiceUnavailable, DriverError) as e:
            logger.error(f"Failed to connect to Neo4J: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4J: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Close connection to Neo4J"""
        if self._driver:
            self._driver.close()
            logger.info("Disconnected from Neo4J")

    def is_connected(self) -> bool:
        """Check if connected to Neo4J"""
        return self._connected and self._driver is not None

    def get_session(self) -> Optional[Session]:
        """Get a Neo4J session"""
        if self._driver:
            return self._driver.session()
        return None

    def create_user(
        self,
        user_id: int,
        email: str,
        first_name: str,
        last_name: str,
        roles: list[str],
    ) -> dict:
        """Create a user node in Neo4J"""
        with self.get_session() as session:
            query = """
            CREATE (u:User {
                id: $id,
                email: $email,
                firstName: $firstName,
                lastName: $lastName
            })
            WITH u
            FOREACH (role_name IN $roles | 
                MERGE (r:Role {name: role_name})
                CREATE (u)-[:HAS_ROLE]->(r)
            )
            RETURN u
            """

            result = session.run(
                query,
                id=user_id,
                email=email,
                firstName=first_name,
                lastName=last_name,
                roles=roles,
            )

            record = result.single()
            if record:
                user_node = record["u"]
                return {
                    "id": user_node["id"],
                    "email": user_node["email"],
                    "firstName": user_node["firstName"],
                    "lastName": user_node["lastName"],
                    "roles": roles,
                }
            return None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        with self.get_session() as session:
            query = """
            MATCH (u:User {id: $id})
            OPTIONAL MATCH (u)-[r:HAS_ROLE]->(role:Role)
            WITH u, collect(role.name) AS roles
            RETURN u {id: u.id, email: u.email, firstName: u.firstName, lastName: u.lastName} AS user,
                   roles
            """

            result = session.run(query, id=user_id)
            record = result.single()

            if record:
                user_data = record["user"]
                roles = record["roles"] or []
                return {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "firstName": user_data["firstName"],
                    "lastName": user_data["lastName"],
                    "roles": roles,
                }
            return None

    def get_all_users(self) -> list[dict]:
        """Get all users"""
        with self.get_session() as session:
            query = """
            MATCH (u:User)
            OPTIONAL MATCH (u)-[r:HAS_ROLE]->(role:Role)
            WITH u, collect(role.name) AS roles
            RETURN u {id: u.id, email: u.email, firstName: u.firstName, lastName: u.lastName} AS user,
                   roles
            ORDER BY u.id
            """

            result = session.run(query)
            users = []

            for record in result:
                user_data = record["user"]
                roles = record["roles"] or []
                users.append(
                    {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "firstName": user_data["firstName"],
                        "lastName": user_data["lastName"],
                        "roles": roles,
                    }
                )

            return users

    def get_users_with_super_seller(self) -> list[dict]:
        """Get users who have super seller status"""
        with self.get_session() as session:
            query = """
            MATCH (u:User)-[:IS_SUPER_SELLER]->(ss:SuperSeller)
            OPTIONAL MATCH (u)-[r:HAS_ROLE]->(role:Role)
            WITH u, ss, collect(role.name) AS roles
            RETURN u {id: u.id, email: u.email, firstName: u.firstName, lastName: u.lastName} AS user,
                   ss.id AS superSellerId,
                   roles
            ORDER BY u.id
            """

            result = session.run(query)
            users = []

            for record in result:
                user_data = record["user"]
                roles = record["roles"] or []
                users.append(
                    {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "firstName": user_data["firstName"],
                        "lastName": user_data["lastName"],
                        "roles": roles,
                        "superSellerId": record["superSellerId"],
                    }
                )

            return users

    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        with self.get_session() as session:
            query = "MATCH (u:User {email: $email}) RETURN COUNT(u) AS count"
            result = session.run(query, email=email)
            count = result.single()["count"]
            return count > 0

    def initialize_database(self):
        """Initialize database with indexes and constraints"""
        with self.get_session() as session:
            # Create constraints
            try:
                session.run(
                    "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE"
                )
            except Exception as e:
                logger.warning(f"Could not create id constraint: {e}")

            try:
                session.run(
                    "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE"
                )
            except Exception as e:
                logger.warning(f"Could not create email constraint: {e}")

            try:
                session.run(
                    "CREATE CONSTRAINT role_name IF NOT EXISTS FOR (r:Role) REQUIRE r.name IS UNIQUE"
                )
            except Exception as e:
                logger.warning(f"Could not create role constraint: {e}")

            # Create indexes
            try:
                session.run("CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email)")
            except Exception as e:
                logger.warning(f"Could not create email index: {e}")

            logger.info("Database initialization completed")

    def update_user(
        self, user_id: int, email: str, first_name: str, last_name: str, roles: list[str]
    ) -> dict:
        """Update a user node in Neo4J"""
        with self.get_session() as session:
            query = """
            MATCH (u:User {id: $id})
            SET u.email = $email,
                u.firstName = $firstName,
                u.lastName = $lastName
            WITH u
            OPTIONAL MATCH (u)-[r:HAS_ROLE]->(:Role)
            DELETE r
            WITH u
            FOREACH (role_name IN $roles |
                MERGE (r:Role {name: role_name})
                CREATE (u)-[:HAS_ROLE]->(r)
            )
            RETURN u
            """

            result = session.run(
                query,
                id=user_id,
                email=email,
                firstName=first_name,
                lastName=last_name,
                roles=roles,
            )

            record = result.single()
            if record:
                user_node = record["u"]
                return {
                    "id": user_node["id"],
                    "email": user_node["email"],
                    "firstName": user_node["firstName"],
                    "lastName": user_node["lastName"],
                    "roles": roles,
                }
            return None

    def delete_user(self, user_id: int):
        """Delete a user node in Neo4J"""
        with self.get_session() as session:
            query = """
            MATCH (u:User {id: $id})
            DETACH DELETE u
            """

            session.run(query, id=user_id)
            logger.info(f"User {user_id} deleted from database")
