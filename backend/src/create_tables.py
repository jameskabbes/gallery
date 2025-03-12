from gallery import models, client

if __name__ == '__main__':
    c = client.Client()
    with c.Session() as session:
        models.BaseDB.metadata.create_all(c.db_engine)
        session.commit()
