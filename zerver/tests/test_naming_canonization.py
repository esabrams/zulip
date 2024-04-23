from zerver.models import Stream
from zerver.lib.test_classes import ZulipTestCase
from zerver.models.streams import get_stream


class NamingTest(ZulipTestCase):
    def test_rename_stream(self) -> None:
        user_profile = self.example_user("hamlet")
        self.login_user(user_profile)
        realm = user_profile.realm
        # Create stream_name1
        stream = self.subscribe(user_profile, "stream_name1")

        # Changes stream_name1 to stream name1
        # Differs in' ' / '-' only -- this should succeed (name duplication prevention not yet implemented)
        result = self.client_patch(f"/json/streams/{stream.id}", {"new_name": "stream name1"})
        self.assert_json_success(result)

        # Changes stream name 1 back to stream_name1 to test stream_name update and notification message
        with self.capture_send_event_calls(expected_num_events=2) as events:
            stream_id = get_stream("stream_name1", user_profile.realm).id
            result = self.client_patch(f"/json/streams/{stream_id}", {"new_name": "stream_name1"})
        self.assert_json_success(result)
        event = events[0]["event"]
        self.assertEqual(
            event,
            dict(
                op="update",
                type="stream",
                property="name",
                value="stream_name1",
                stream_id=stream_id,
                name="stream name1",
            ),
        )

        # Tests stream name 1 no longer exists
        self.assertRaises(Stream.DoesNotExist, get_stream, "stream name1", realm)

        # Tests stream_name1 properly applied
        stream_name1_exists = get_stream("stream_name1", realm)
        self.assertTrue(stream_name1_exists)
