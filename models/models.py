from couchdb.mapping import(
    TextField,
    ListField,
    DateTimeField,
    BooleanField
)

from .BaseDocument import BaseDocument
from .DBManager import DBManager

import datetime
import uuid

class Complaint(BaseDocument):
    ALL_STATUS = ["waiting","resolved", "rejected"]
    post_id = TextField()
    text = TextField()
    timestamp = DateTimeField()
    status = TextField()
    complainant_id = TextField()
    department_ids = ListField(TextField())
    comment_ids = ListField(TextField())

    def get_status(self):
        return self.status

    def set_status(self, status):
        if(status in self.ALL_STATUS):
            self.status = status
            self.save()
        else:
            raise ValueError(
                "Status value can be waiting, resolved or rejected"
            )

    def get_complainant(self):
        db = DBManager.db()
        complainant = Complainant.load(db, self.complainant_id)
        return complainant

    def get_comments(self):
        db = DBManager.db()
        comments = [Comment.load(db, i) for i in self.comment_ids]
        return comments

    def get_departments(self):
        DBManager.db()
        departments = [Department.load(db, i) for i in self.department_ids]
        return departments

    @classmethod
    def get_by_timestamp(cls, skip, limit):
        db = DBManager.db()
        complaints = []
        rows = db.view(
            'views/complaintByTimestamp',
            limit=limit,
            skip=skip,
            descending=True,
            include_docs=True
        )
        for row in rows:
            complaints.append(cls.load(db, row.doc.id))
        return complaints


class Complainant(BaseDocument):
    account_type = TextField()
    account_handle = TextField()
    complaint_ids = ListField(TextField())

    def get_complaints(self):
        db = DBManager.db()
        complaints = [Complaint.load(db, i) for i in self.complaint_ids]
        return complaints

    @classmethod
    def search_complainant(cls,account_handle, account_type):
        db = DBManager.db()
        c = db.view(
            'views/complainantByHandle',
            key=account_handle,
            include_docs=True
        )
        for row in c:
            if row.doc['account_type'] == account_type:
                return cls.load(db, row.doc.id)
        return None

    @classmethod
    def get_or_create_complainant(cls, account_handle, account_type):
        complainant = cls.search_complainant(
            account_handle,
            account_type
        )
        if(complainant is None):
            complainant = cls(
                account_handle=account_handle,
                account_type=account_type,
                complaint_ids=[]
            )
        return complainant


class Department(BaseDocument):
    name = TextField()
    subdepartment_ids = ListField(TextField())
    parent_department_id = TextField()
    supervisor_ids = ListField(TextField())
    complaint_ids = ListField(TextField())

    def get_subdepartments(self):
        db = DBManager.db()
        subdepartments = [Department.load(db, i) for i in self.subdepartment_ids]
        return subdepartments

    def get_parent_department(self):
        db = DBManager.db()
        parent_department = Department.load(db, self.parent_department_id)
        return parent_department

    def get_supervisors(self):
        db = DBManager.db()
        supervisors = [Supervisor.load(db, i) for i in self.supervisor_ids]
        return supervisors

    def get_complaints(self):
        db = DBManager.db()
        complaints = [Complaint.load(db, i) for i in self.complaint_ids]

class PasswordRecovery(BaseDocument):

    supervisor_id = TextField()
    token = TextField()
    timestamp = DateTimeField()
    used = BooleanField()

    def get_supervisor(self):
        db = DBManager.db()
        supervisor = Supervisor.load(db, self.supervisor_id)
        return supervisor

    def recover_password(self, token, new_password):
        if(token == self.token):
            supervisor = self.get_supervisor()
            db = DBManager.db()
            supervisor.password = new_password
            supervisor.password_recovery_id = None
            supervisor.store(db)
            self.used = True
            self.save()
            return True
        return False

class Supervisor(BaseDocument):
    email = TextField()
    password = TextField()
    name = TextField()
    designation = TextField()
    department_ids = ListField(TextField())
    password_recovery_id = TextField()

    @classmethod
    def search_supervisor(cls, email):
        db = DBManager.db()
        s = db.view(
            'views/supervisorByEmail',
            key=email,
            include_docs=True
        )
        for row in s:
            return cls.load(db, row.doc.id)
        return None

    def authenticate(self, password):
        if self.password == password:
            return True
        return False

    def get_password_recovery(self):
        db = DBManager.db()
        if(self.password_recovery_id is not None):
            return PasswordRecovery.load(
                db,
                self.password_recovery_id
            )

        return None

    def create_password_recovery(self):
        db = DBManager.db()
        timestamp = datetime.datetime.now()
        token = str(uuid.uuid4().hex.upper()[0:6])
        pr = PasswordRecovery(
            supervisor_id=self.id,
            token=token,
            timestamp=timestamp,
            used=False
        )
        pr.store(db)
        self.password_recovery_id = pr.id
        self.store(db)
        return pr
        # Send Email Notification

class Comment(BaseDocument):
    text = TextField()
    timestamp = DateTimeField()
    post_id = TextField()
    complaint_id = TextField()
    prev_comment_id = TextField()

    def get_complaint(self):
        db = DBManager.db()
        complaint = Complaint.load(db, self.complaint_id)
        return complaint

    def get_prev_comment(self):
        db = DBManager.db()
        if(self.prev_comment_id == None):
            return None
        return self.load(db, self.prev_comment_id)

    @classmethod
    def create_comment(cls, complaint, *args, **kwargs):
        comment = cls(
            *args,
            complaint_id=complaint.id,
            **kwargs
        )
        comment.save()
        complaint.comment_ids.push(comment.id)
        complaint.save()
