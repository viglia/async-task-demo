import time
from task_app.views import JobList

import pytest
from rest_framework.response import Response


@pytest.mark.usefixtures('live_server')
class IntegrationTests:

    def test_task_ends(self, rf, mocker):
        mocker.patch(
            'task_app.views.JobList.get_sleep_time',
            return_value=0
        )
        request = rf.post('/api/jobs', {'object_id': 1})
        response: Response = JobList.as_view()(request)
        assert response.status_code == 201

        job_id = response.data["id"]
        time.sleep(2)

        request = rf.get(f'/api/jobs/{job_id}')
        response: Response = JobList.as_view()(request)
        assert response.data[0]["job_status"] == "EN"

    def test_same_job_id_within_5_min(self, rf, mocker):
        mocker.patch(
            'task_app.views.JobList.get_sleep_time',
            return_value=0
        )
        request = rf.post('/api/jobs', {'object_id': 2})
        response: Response = JobList.as_view()(request)
        assert response.status_code == 201
        first_id = response.data["id"]

        request = rf.post('/api/jobs', {'object_id': 2})
        response: Response = JobList.as_view()(request)
        assert response.status_code == 200
        second_id = response.data["id"]

        assert first_id == second_id

    def test_same_job_id_after_5_min(self, rf, mocker):
        mocker.patch(
            'task_app.views.JobList.get_sleep_time',
            return_value=0
        )
        mocker.patch(
            'task_app.views.JobList.recent_job_exists',
            return_value=(False, None)
        )

        request = rf.post('/api/jobs', {'object_id': 3})
        response: Response = JobList.as_view()(request)
        assert response.status_code == 201
        first_id = response.data["id"]

        request = rf.post('/api/jobs', {'object_id': 3})
        response: Response = JobList.as_view()(request)
        assert response.status_code == 201
        second_id = response.data["id"]

        time.sleep(1)
        assert first_id != second_id

    def test_job_reload_on_consumer_failure(self):
        pass
