from src.core.database import Base, engine

import src.models.user
import src.models.poll_group
import src.models.poll
import src.models.poll_option
import src.models.vote

Base.metadata.create_all(bind=engine)