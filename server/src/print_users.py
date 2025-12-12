from src.database import SessionLocal
from src import models
s=SessionLocal()
users=s.query(models.User).limit(20).all()
for u in users:
    print('User',u.UserID,u.Email,u.Name,'CareerID',u.CareerLevelID,'ExpRange',u.ExperienceRangeID)
    print(' Skills:',[sk.SkillName for sk in u.skills])
    print(' Desired:',[dj.JobName for dj in u.desired_jobs])
s.close()
