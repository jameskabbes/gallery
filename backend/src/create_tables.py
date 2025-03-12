from sqlalchemy.orm import sessionmaker
from gallery import models, client

if __name__ == '__main__':
    c = client.Client()
    with sessionmaker(c.db_engine)() as session:
        models.BaseDB.metadata.create_all(c.db_engine)
        session.commit()
