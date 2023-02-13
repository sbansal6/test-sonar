def dog_test_task(
        self,
        dog_func,
        ≈,
        dog_type: str,
    ) -> None:
        if not dogs:
            return

        esp = dogs[0].esp
        vendor = esp.text_id if esp else "internal"
        with statsd.timer(
            DOG_PUBLISH_KEY.format(type=dog_type, vendor=vendor),
            rate=100,
        ):
            roller_id_to_dogs = defaultdict(list)
            for dog in dogs:
                roller_id_to_dogs[dog.id].append(dog)

            for dog_id, dog_events in roller_id_to_dogs.items():
                batch_size = self._get_batch_size(len(roller_id_to_dogs))
                for dog_batch in grouper(roller_id_to_dogs, batch_size):
                    serialized_dogs = [e.to_dict() for e in dog_batch]
                enqueue_func(serialized_dogs, 123)
