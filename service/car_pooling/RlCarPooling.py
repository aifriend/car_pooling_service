from car_pooling.IService import IService


class CarPooling(IService):
    BAD_REQUEST = -1
    NOT_ALLOCATED = 0
    MAX_SEAT = 6

    def __init__(self, _car_pooling=None):
        """
        Class for car pooling service

        :param _car_pooling: Car pooling list (format: [(1,1),(2,2),...])
        """
        if _car_pooling is None:
            _car_pooling = dict()
        if isinstance(_car_pooling, dict):
            self.car_pooling = _car_pooling
        self.car_pooling = dict(_car_pooling)

        car_pooling_clean = self.car_pooling.copy()
        for car_id, car_seat in self.car_pooling.items():
            if not self._is_valid(car_id, car_seat):
                del car_pooling_clean[car_id]
        self.car_pooling = car_pooling_clean
        self.journey_request = self.JourneyRequest()
        self.journey_location = self.JourneyLocation()

    def status(self):
        pass

    def cars(self, _car_pooling):
        if _car_pooling is None:
            return None
        if isinstance(_car_pooling, dict):
            self.car_pooling = _car_pooling
        self.car_pooling = dict(_car_pooling)

    def add(self, car_id, car_seats):
        try:
            self.car_pooling[car_id] = car_seats
            return car_id
        except Exception:
            return None

    def journey(self, journey_id, journey_passenger):
        # journey waiting list first
        if len(self.journey_request.waiting) > 0:
            for waiting_id, waiting_seat in self.journey_request.waiting.copy().items():
                # waiting car found to fulfill journey request
                best_waiting_car_id = self._try_journey(waiting_id, waiting_seat)
                if best_waiting_car_id and \
                        best_waiting_car_id != self.NOT_ALLOCATED and \
                        best_waiting_car_id != self.BAD_REQUEST:
                    self.car_pooling.pop(best_waiting_car_id)
                    self.journey_request.remove(waiting_id)
                    self.journey_location.add(journey_id=journey_id, car_id=best_waiting_car_id)

        # actual journey request
        best_car_id = self._try_journey(journey_id, journey_passenger)
        if best_car_id == self.BAD_REQUEST:  # not valid
            return self.BAD_REQUEST
        if best_car_id == self.NOT_ALLOCATED:  # not availability: add to waiting list
            self.journey_request.add(journey_id=journey_id, passenger=journey_passenger)
            return self.NOT_ALLOCATED
        else:  # journey request allocated
            self.car_pooling.pop(best_car_id)
            self.journey_location.add(journey_id=journey_id, car_id=best_car_id)
            return best_car_id

    def drop_off(self, journey_id):
        return self.journey_request.remove(journey_id)

    def location(self, journey_id):
        self.journey_location.is_allocated(journey_id)
