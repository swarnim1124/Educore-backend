"""
File: xsc_libc_pgrs.py
Description: OneApp Common PostgreSQL Library - Abstraction layer for database operations.

Author: Siddharth Amdal
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

import os
from sqlalchemy import (
    create_engine,
    text,
    table,
    column,
    select as sa_select,
    update as sa_update,
    delete as sa_delete,
    insert as sa_insert,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class PostgreSQLManager:
    """
    Singleton PostgreSQL Manager for handling all database operations.

    This class acts as the single entry point for all PostgreSQL database
    interactions within the OneApp Backend. It wraps SQLAlchemy 2.x Core
    and psycopg3 (sync) / asyncpg (async) to provide a connection pool and
    simplified CRUD methods that return a standard dictionary response envelope.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgreSQLManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.engine = None
        self.async_engine = None
        self.async_session_maker = None
        self.config = {}

        self.errCode = ""
        self.errMsg = ""

        self.loadConfig()
        self._initialized = True

    def _setError(self, code, msg):
        self.errCode = str(code)
        self.errMsg = str(msg)

    def _clearError(self):
        self.errCode = ""
        self.errMsg = ""

    def _buildErrorResponse(self, default_message):
        return XSCUtility.error_response(
            message=default_message, error_code=self.errCode
        )

    def _buildSuccessResponse(self, message="Operation Successful", data=None):
        response = XSCUtility.success_response(message=message)
        if data is not None:
            response["data"] = data
        else:
            response["data"] = {}
        return response

    def loadConfig(self, config_file="xsc_conf/xsc_conf_pgrs.json"):
        import json

        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
        except Exception as e:
            print(
                f"[PostgreSQLManager] Warning: Failed to load config from {config_file}: {e}"
            )

    # ==========================================
    # SYNC METHODS
    # ==========================================

    def connectDB(self):
        self._clearError()
        if self.engine:
            return self._buildSuccessResponse("Already connected")

        try:
            conn_url = f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"

            connect_args = {}
            if self.config.get("sslmode"):
                connect_args["sslmode"] = self.config["sslmode"]

            self.engine = create_engine(
                conn_url,
                poolclass=QueuePool,
                pool_size=self.config.get("maxconn", 10),
                max_overflow=0,
                connect_args=connect_args,
            )

            return self._buildSuccessResponse("Connected to database successfully")
        except Exception as e:
            self._setError("UNKNOWN", str(e))
            return self._buildErrorResponse("Database connection failed")

    def disconnectDB(self):
        self._clearError()
        if self.engine:
            try:
                self.engine.dispose()
                self.engine = None
                return self._buildSuccessResponse(
                    "Disconnected from database successfully"
                )
            except Exception as e:
                self._setError("UNKNOWN", str(e))
                return self._buildErrorResponse("Database disconnection failed")
        return self._buildSuccessResponse("Not connected")

    def healthCheck(self):
        self._clearError()
        if not self.engine:
            return self.connectDB()

        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return self._buildSuccessResponse("Database connection is healthy")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            self.disconnectDB()
            return self.connectDB()

    def getConnection(self):
        self._clearError()
        if not self.engine:
            return self._buildErrorResponse("Connection pool not initialized")

        try:
            conn = self.engine.connect()
            return conn
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Failed to get connection from pool")

    def releaseConnection(self, conn):
        if self.engine and conn:
            try:
                conn.close()
                return self._buildSuccessResponse("Connection released successfully")
            except SQLAlchemyError as e:
                self._setError(
                    (
                        getattr(e.orig, "sqlstate", "UNKNOWN")
                        if hasattr(e, "orig")
                        else "UNKNOWN"
                    ),
                    str(e),
                )
                return self._buildErrorResponse("Failed to release connection")
        return self._buildErrorResponse("Pool not initialized or conn is invalid")

    def poolStatus(self):
        if self.engine:
            pool = self.engine.pool
            return self._buildSuccessResponse(
                "Pool status retrieved",
                {
                    "minconn": self.config.get("minconn", 1),
                    "maxconn": pool.size(),
                    "checkedin": pool.checkedin(),
                    "checkedout": pool.checkedout(),
                },
            )
        return self._buildErrorResponse("Connection pool not initialized")

    def beginTransaction(self, conn=None):
        if not conn:
            return self._buildErrorResponse(
                "A connection object must be provided to begin transaction"
            )

        try:
            if not conn.in_transaction():
                conn.begin()
            return self._buildSuccessResponse("Transaction begun successfully")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Failed to begin transaction")

    def commit(self, conn=None):
        if not conn:
            return self._buildErrorResponse(
                "A connection object must be provided to commit transaction"
            )

        try:
            conn.commit()
            return self._buildSuccessResponse("Transaction committed successfully")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Failed to commit transaction")

    def rollback(self, conn=None):
        if not conn:
            return self._buildErrorResponse(
                "A connection object must be provided to rollback transaction"
            )

        try:
            conn.rollback()
            return self._buildSuccessResponse("Transaction rolled back successfully")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Failed to rollback transaction")

    def insert(self, tableName, data):
        self._clearError()
        if not data:
            return self._buildErrorResponse("No data provided for insert")

        cols = [column(k) for k in data.keys()]
        t = table(tableName, *cols)
        stmt = sa_insert(t).values(**data).returning(text("*"))

        return self._executePrepared(stmt)

    def update(self, tableName, data, where):
        self._clearError()
        if not data or not where:
            return self._buildErrorResponse(
                "Data and where clauses are required for update"
            )

        cols = [column(k) for k in list(data.keys()) + list(where.keys())]
        t = table(tableName, *cols)

        stmt = sa_update(t).values(**data)
        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = stmt.returning(text("*"))
        return self._executePrepared(stmt)

    def delete(self, tableName, where):
        self._clearError()
        if not where:
            return self._buildErrorResponse("Where clause is required for delete")

        cols = [column(k) for k in where.keys()]
        t = table(tableName, *cols)

        stmt = sa_delete(t)
        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = stmt.returning(text("*"))
        return self._executePrepared(stmt)

    def select(self, columns, tableName, where=None):
        self._clearError()

        if columns and len(columns) > 0 and columns[0] != "*":
            cols = [column(c) for c in columns]
            t = table(
                tableName,
                *(cols + [column(k) for k in (where.keys() if where else [])]),
            )
            stmt = sa_select(*cols).select_from(t)
        else:
            t = table(tableName, *[column(k) for k in (where.keys() if where else [])])
            stmt = sa_select(text("*")).select_from(t)

        if where:
            for k, v in where.items():
                stmt = stmt.where(column(k) == v)

        return self._executePrepared(stmt)

    def exists(self, tableName, where):
        self._clearError()
        if not where:
            return self._buildErrorResponse("Where clause is required for exists")

        t = table(tableName, *[column(k) for k in where.keys()])
        stmt = sa_select(text("1")).select_from(t)

        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = sa_select(stmt.exists())

        result = self._executePrepared(stmt)
        if result["status"] == "success":
            exists_flag = result["data"][0]["exists"] if result["data"] else False
            return self._buildSuccessResponse("Exists checked", {"exists": exists_flag})
        return result

    def count(self, tableName, where=None):
        self._clearError()

        t = table(tableName, *[column(k) for k in (where.keys() if where else [])])
        stmt = sa_select(text("COUNT(*)")).select_from(t)

        if where:
            for k, v in where.items():
                stmt = stmt.where(column(k) == v)

        result = self._executePrepared(stmt)
        if result["status"] == "success":
            count_val = result["data"][0]["count"] if result["data"] else 0
            return self._buildSuccessResponse("Count retrieved", {"count": count_val})
        return result

    def genericSQL(self, sqlStatement, params=None):
        if isinstance(sqlStatement, str):
            sqlStatement = text(sqlStatement)
        return self._executePrepared(sqlStatement, params)

    def _executePrepared(self, query, params=None):
        self._clearError()
        conn = self.getConnection()
        if isinstance(conn, dict) and conn.get("status") == "error":
            return conn

        try:
            if isinstance(query, str):
                result = conn.exec_driver_sql(query, params)
            else:
                result = conn.execute(query, params or {})

            if result.returns_rows:
                data = [dict(row) for row in result.mappings().all()]
                conn.commit()
                return self._buildSuccessResponse("Query executed successfully", data)
            else:
                conn.commit()
                return self._buildSuccessResponse("Query executed successfully")
        except SQLAlchemyError as e:
            conn.rollback()
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Database Operation Failed")
        except Exception as e:
            conn.rollback()
            self._setError("UNKNOWN", str(e))
            return self._buildErrorResponse("Database Operation Failed")
        finally:
            self.releaseConnection(conn)

    # ==========================================
    # ASYNC METHODS
    # ==========================================

    async def async_connectDB(self):
        self._clearError()
        if self.async_engine:
            return self._buildSuccessResponse("Already connected to async pool")

        try:
            conn_url = f"postgresql+asyncpg://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"

            self.async_engine = create_async_engine(
                conn_url, pool_size=self.config.get("maxconn", 10), max_overflow=0
            )
            self.async_session_maker = async_sessionmaker(
                self.async_engine, expire_on_commit=False, class_=AsyncSession
            )

            return self._buildSuccessResponse(
                "Connected to async database successfully"
            )
        except Exception as e:
            self._setError("UNKNOWN", str(e))
            return self._buildErrorResponse("Async database connection failed")

    async def async_disconnectDB(self):
        self._clearError()
        if self.async_engine:
            try:
                await self.async_engine.dispose()
                self.async_engine = None
                self.async_session_maker = None
                return self._buildSuccessResponse(
                    "Disconnected from async database successfully"
                )
            except Exception as e:
                self._setError("UNKNOWN", str(e))
                return self._buildErrorResponse("Async database disconnection failed")
        return self._buildSuccessResponse("Not connected")

    async def async_healthCheck(self):
        self._clearError()
        if not self.async_engine:
            await self.async_connectDB()

        try:
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return self._buildSuccessResponse("Async database connection is healthy")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            await self.async_disconnectDB()
            await self.async_connectDB()
            return self._buildErrorResponse(
                "Async database connection failed health check"
            )

    async def async_insert(self, tableName, data):
        self._clearError()
        if not data:
            return self._buildErrorResponse("No data provided for insert")

        cols = [column(k) for k in data.keys()]
        t = table(tableName, *cols)
        stmt = sa_insert(t).values(**data).returning(text("*"))

        return await self._async_executePrepared(stmt)

    async def async_update(self, tableName, data, where):
        self._clearError()
        if not data or not where:
            return self._buildErrorResponse(
                "Data and where clauses are required for update"
            )

        cols = [column(k) for k in list(data.keys()) + list(where.keys())]
        t = table(tableName, *cols)

        stmt = sa_update(t).values(**data)
        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = stmt.returning(text("*"))
        return await self._async_executePrepared(stmt)

    async def async_delete(self, tableName, where):
        self._clearError()
        if not where:
            return self._buildErrorResponse("Where clause is required for delete")

        cols = [column(k) for k in where.keys()]
        t = table(tableName, *cols)

        stmt = sa_delete(t)
        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = stmt.returning(text("*"))
        return await self._async_executePrepared(stmt)

    async def async_select(self, columns, tableName, where=None):
        self._clearError()

        if columns and len(columns) > 0 and columns[0] != "*":
            cols = [column(c) for c in columns]
            t = table(
                tableName,
                *(cols + [column(k) for k in (where.keys() if where else [])]),
            )
            stmt = sa_select(*cols).select_from(t)
        else:
            t = table(tableName, *[column(k) for k in (where.keys() if where else [])])
            stmt = sa_select(text("*")).select_from(t)

        if where:
            for k, v in where.items():
                stmt = stmt.where(column(k) == v)

        return await self._async_executePrepared(stmt)

    async def async_exists(self, tableName, where):
        self._clearError()
        if not where:
            return self._buildErrorResponse("Where clause is required for exists")

        t = table(tableName, *[column(k) for k in where.keys()])
        stmt = sa_select(text("1")).select_from(t)

        for k, v in where.items():
            stmt = stmt.where(column(k) == v)

        stmt = sa_select(stmt.exists())

        result = await self._async_executePrepared(stmt)
        if result["status"] == "success":
            exists_flag = result["data"][0]["exists"] if result["data"] else False
            return self._buildSuccessResponse("Exists checked", {"exists": exists_flag})
        return result

    async def async_count(self, tableName, where=None):
        self._clearError()

        t = table(tableName, *[column(k) for k in (where.keys() if where else [])])
        stmt = sa_select(text("COUNT(*)")).select_from(t)

        if where:
            for k, v in where.items():
                stmt = stmt.where(column(k) == v)

        result = await self._async_executePrepared(stmt)
        if result["status"] == "success":
            count_val = result["data"][0]["count"] if result["data"] else 0
            return self._buildSuccessResponse("Count retrieved", {"count": count_val})
        return result

    async def async_genericSQL(self, sqlStatement, params=None):
        if isinstance(sqlStatement, str):
            sqlStatement = text(sqlStatement)
        return await self._async_executePrepared(sqlStatement, params)

    async def _async_executePrepared(self, query, params=None):
        self._clearError()
        if not self.async_engine:
            return self._buildErrorResponse("Async connection pool not initialized")

        try:
            async with self.async_engine.begin() as conn:
                if isinstance(query, str):
                    result = await conn.exec_driver_sql(query, params)
                else:
                    result = await conn.execute(query, params or {})

                if result.returns_rows:
                    data = [dict(row) for row in result.mappings().all()]
                    return self._buildSuccessResponse(
                        "Query executed successfully", data
                    )
                else:
                    return self._buildSuccessResponse("Query executed successfully")
        except SQLAlchemyError as e:
            self._setError(
                (
                    getattr(e.orig, "sqlstate", "UNKNOWN")
                    if hasattr(e, "orig")
                    else "UNKNOWN"
                ),
                str(e),
            )
            return self._buildErrorResponse("Database Operation Failed")
        except Exception as e:
            self._setError("UNKNOWN", str(e))
            return self._buildErrorResponse("Database Operation Failed")
