from config import ScraperConfig

import psycopg2

class ScraperQuery:
    @staticmethod
    def execute_one(query, args=None):
        return ScraperQuery.execute(query, args, 1)
    
    @staticmethod
    def execute(query, args=None, count=0):
        with psycopg2.connect(**ScraperConfig.DATABASE_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(query, args)
                if count <= 0:
                    return cur.fetchall()
                if count == 1:
                    return cur.fetchone()
                return cur.fetchmany(count)
    
    @staticmethod
    def execute_id(query, args):
        result = ScraperQuery.execute_one(query, args)
        return result.get("id") if result is not None else None
