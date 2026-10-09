from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker

from bearings.models import Client
from bearings.models import Order
from bearings.models import Feedback
from bearings.models import Bearing
from bearings.models import OrderComposition

# Create your tests here.
class OrdersViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):

        clnt = baker.make("bearings.Client")
        order = baker.make("Order", client=clnt)

        r = self.client.get('/api/orders/')
        data = r.json()
        print(data)


        assert order.number == data[0]['number']
        assert order.client.name == data[0]['client']['name']
        assert len(data) == 1


    def test_create_order(self):
        clnt = baker.make("bearings.Client")

        r = self.client.post("/api/orders/", {
            "number": 111111,
            "client_id": clnt.id
        })

        new_order_id = r.json()['id']

        orders = Order.objects.all()
        assert len(orders) == 1

        new_order = Order.objects.filter(id=new_order_id).first()
        assert new_order.number == 111111
        assert new_order.client == clnt 

    def test_delete_order(self):
        orders = baker.make("Order", 10)
        r = self.client.get("/api/orders/")
        data = r.json()
        assert len(data) == 10


        order_id_to_delete = orders[3].id
        self.client.delete(f'/api/orders/{order_id_to_delete}/')

        r = self.client.get("/api/orders/")
        data = r.json()
        assert len(data) == 9

        assert order_id_to_delete not in [i['id'] for i in data] 
    
    def test_update_order(self):
        orders = baker.make("Order", 10)
        order: Order = orders[2]

        r = self.client.get(f'/api/orders/{order.id}/')
        data = r.json()
        assert data['number'] == order.number

        r = self.client.patch(f'/api/orders/{order.id}/', {
            "number": 222222,
        }, format='json')
            
        assert r.status_code == 200

        r = self.client.get(f'/api/orders/{order.id}/')
        data = r.json()
        assert data['number'] == 222222

        order.refresh_from_db()
        assert data['number'] == order.number


class FeedbacksViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):

        clnt = baker.make("bearings.Client")
        feedback = baker.make("Feedback", client=clnt)

        r = self.client.get('/api/feedbacks/')
        data = r.json()
        print(data)


        assert feedback.review == data[0]['review']
        assert feedback.client.name == data[0]['client']['name']
        assert len(data) == 1


    def test_create_feedback(self):
        clnt = baker.make("bearings.Client")

        r = self.client.post("/api/feedbacks/", {
            "review": "ура",
            "client_id": clnt.id
        })

        new_feedback_id = r.json()['id']

        feedbacks = Feedback.objects.all()
        assert len(feedbacks) == 1

        new_feedback = Feedback.objects.filter(id=new_feedback_id).first()
        assert new_feedback.review == "ура"
        assert new_feedback.client == clnt 

    def test_delete_order(self):
        feedbacks = baker.make("Feedback", 10)
        r = self.client.get("/api/feedbacks/")
        data = r.json()
        assert len(data) == 10


        feedback_id_to_delete = feedbacks[3].id
        self.client.delete(f'/api/feedbacks/{feedback_id_to_delete}/')

        r = self.client.get("/api/feedbacks/")
        data = r.json()
        assert len(data) == 9

        assert feedback_id_to_delete not in [i['id'] for i in data] 
    
    def test_update_order(self):
        feedbacks = baker.make("Feedback", 10)
        feedback: Feedback = feedbacks[2]

        r = self.client.get(f'/api/feedbacks/{feedback.id}/')
        data = r.json()
        assert data['review'] == feedback.review

        r = self.client.patch(f'/api/feedbacks/{feedback.id}/', {
            "review": "ура",
        }, format='json')
            
        assert r.status_code == 200

        r = self.client.get(f'/api/feedbacks/{feedback.id}/')
        data = r.json()
        assert data['review'] == "ура"

        feedback.refresh_from_db()
        assert data['review'] == feedback.review



class ClientsViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        clnt = baker.make("bearings.Client")

        r = self.client.get('/api/clients/')
        data = r.json()
        print(data)


        assert clnt.name == data[0]['name']
        assert clnt.phone == data[0]['phone']
        assert len(data) == 1


    def test_create_client(self):
        r = self.client.post("/api/clients/", {
            "name": "Глеб Штырев",
            "phone": "89021709198"
        })

        new_client_id = r.json()['id']

        clients = Client.objects.all()
        assert len(clients) == 1

        new_client = Client.objects.filter(id=new_client_id).first()
        assert new_client.name == "Глеб Штырев"
        assert new_client.phone == "89021709198"

    def test_delete_client(self):
        clients = baker.make("Client", 10)
        r = self.client.get("/api/clients/")
        data = r.json()
        assert len(data) == 10


        client_id_to_delete = clients[3].id
        self.client.delete(f'/api/clients/{client_id_to_delete}/')

        r = self.client.get("/api/clients/")
        data = r.json()
        assert len(data) == 9

        assert client_id_to_delete not in [i['id'] for i in data] 
    
    def test_update_client(self):
        clients = baker.make("Client", 10)
        client: Client = clients[2]

        r = self.client.get(f'/api/clients/{client.id}/')
        data = r.json()
        assert data['name'] == client.name

        r = self.client.patch(f'/api/clients/{client.id}/', {
            "name": "AAA",
        }, format='json')
            
        assert r.status_code == 200

        r = self.client.get(f'/api/clients/{client.id}/')
        data = r.json()
        assert data['name'] == "AAA"

        client.refresh_from_db()
        assert data['name'] == client.name


class BearingsViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        bearing = baker.make("bearings.Bearing")

        r = self.client.get('/api/bearings/')
        data = r.json()
        print(data)


        assert bearing.name == data[0]['name']
        assert bearing.price == data[0]['price']
        assert bearing.ammount == data[0]['ammount']
        assert len(data) == 1


    def test_create_bearing(self):
        r = self.client.post('/api/bearings/', {
            "name": "test",
            "inner_d": 5,
            "outer_d": 5,
            "height": 5,
            "price": 100,
            "ammount": 100
        })

        new_bearing_id = r.json()['id']

        bearings = Bearing.objects.all()
        assert len(bearings) == 1

        new_bearing = Bearing.objects.filter(id=new_bearing_id).first()
        assert new_bearing.name == "test"
        assert new_bearing.price == 100
        assert new_bearing.ammount == 100

    def test_delete_bearing(self):
        bearings = baker.make("Bearing", 10)
        r = self.client.get("/api/bearings/")
        data = r.json()
        assert len(data) == 10


        bearing_id_to_delete = bearings[3].id
        self.client.delete(f'/api/bearings/{bearing_id_to_delete}/')

        r = self.client.get("/api/bearings/")
        data = r.json()
        assert len(data) == 9

        assert bearing_id_to_delete not in [i['id'] for i in data] 
    
    def test_update_bearing(self):
        bearings = baker.make("Bearing", 10)
        bearing: Bearing = bearings[2]

        r = self.client.get(f'/api/bearings/{bearing.id}/')
        data = r.json()
        assert data['name'] == bearing.name

        r = self.client.patch(f'/api/bearings/{bearing.id}/', {
            "name": "AAA",
        }, format='json')
            
        assert r.status_code == 200

        r = self.client.get(f'/api/bearings/{bearing.id}/')
        data = r.json()
        assert data['name'] == "AAA"

        bearing.refresh_from_db()
        assert data['name'] == bearing.name



class OrderCompositionViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        order = baker.make("bearings.Order")
        bearing = baker.make("bearings.Bearing")
        oc = baker.make("bearings.OrderComposition", order=order, bearing=bearing)

        r = self.client.get('/api/ordersCompositions/')
        data = r.json()
        print(data)


        assert oc.ammount == data[0]['ammount']
        assert len(data) == 1


    def test_create_oc(self):
        ordr = baker.make("bearings.Order")
        brng = baker.make("bearings.Bearing")

        r = self.client.post('/api/ordersCompositions/', {
            "order_id": ordr.id,
            "bearing_id": brng.id,
            "ammount": 100
        })

        new_oc_id = r.json()['id']

        ocs = OrderComposition.objects.all()
        assert len(ocs) == 1

        new_oc = OrderComposition.objects.filter(id=new_oc_id).first()
        assert new_oc.ammount == 100
        assert new_oc.order == ordr
        assert new_oc.bearing == brng

    def test_delete_oc(self):
        ocs = baker.make("OrderComposition", 10)
        r = self.client.get("/api/ordersCompositions/")
        data = r.json()
        assert len(data) == 10


        oc_id_to_delete = ocs[3].id
        self.client.delete(f'/api/ordersCompositions/{oc_id_to_delete}/')

        r = self.client.get("/api/ordersCompositions/")
        data = r.json()
        assert len(data) == 9

        assert oc_id_to_delete not in [i['id'] for i in data] 
    
    def test_update_oc(self):
        ocs = baker.make("OrderComposition", 10)
        oc: OrderComposition = ocs[2]

        r = self.client.get(f'/api/ordersCompositions/{oc.id}/')
        data = r.json()
        assert data['ammount'] == oc.ammount

        r = self.client.patch(f'/api/ordersCompositions/{oc.id}/', {
            "ammount": 120,
        }, format='json')
            
        assert r.status_code == 200

        r = self.client.get(f'/api/ordersCompositions/{oc.id}/')
        data = r.json()
        assert data['ammount'] == 120

        oc.refresh_from_db()
        assert data['ammount'] == oc.ammount
