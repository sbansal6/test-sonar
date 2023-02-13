def _publish_preprocessing_task(
        self,
        enqueue_func: Callable[[list[dict], str], None],
        events: list[EmailEventIngest],
        event_type: str,
    ) -> None:
        if not events:
            return

        esp = events[0].esp
        vendor = esp.text_id if esp else "internal"
        with statsd.timer(
            EVENT_PUBLISH_KEY.format(type=event_type, vendor=vendor),
            rate=EMAIL_EVENTS_STAT_SAMPLE_RATE,
        ):
            company_id_to_events = defaultdict(list)
            for event in events:
                company_id_to_events[event.company_id].append(event)

            for company_id, company_events in company_id_to_events.items():
                batch_size = self._get_batch_size(len(company_events))
                for event_batch in grouper(company_events, batch_size):
                    serialized_events = [e.to_dict() for e in event_batch]
                enqueue_func(serialized_events, company_id)

        statsd.incr(
            WEBHOOK_RECEIVED_KEY.format(vendor=vendor if vendor else "unknown"),
            len(events),
        )
