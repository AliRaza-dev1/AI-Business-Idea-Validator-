import api, { auth, ideas, analysis, reports, dashboard } from '../services/api';
import MockAdapter from 'axios-mock-adapter';

describe('API Services', () => {
  let mock;

  beforeAll(() => {
    mock = new MockAdapter(api);
  });

  afterEach(() => {
    mock.reset();
  });

  afterAll(() => {
    mock.restore();
  });

  describe('Auth Service', () => {
    it('register should send POST to /auth/register', async () => {
      const mockData = { id: 1, email: 'test@example.com' };
      mock.onPost('/auth/register').reply(201, mockData);

      const response = await auth.register('test@example.com', 'password123');
      expect(response.data).toEqual(mockData);
      expect(JSON.parse(mock.history.post[0].data)).toEqual({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    it('login should send POST to /auth/login', async () => {
      const mockData = { access_token: 'fake-token' };
      mock.onPost('/auth/login').reply(200, mockData);

      const response = await auth.login('test@example.com', 'password123');
      expect(response.data).toEqual(mockData);
      expect(JSON.parse(mock.history.post[0].data)).toEqual({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    it('getCurrentUser should send GET to /auth/me', async () => {
      mock.onGet('/auth/me').reply(200, { email: 'me@example.com' });
      const response = await auth.getCurrentUser();
      expect(response.data.email).toEqual('me@example.com');
    });
  });

  describe('Ideas Service', () => {
    it('create should send POST to /ideas/', async () => {
      const ideaData = { title: 'Test Idea' };
      mock.onPost('/ideas/').reply(201, ideaData);

      const response = await ideas.create(ideaData);
      expect(response.data).toEqual(ideaData);
    });

    it('getAll should send GET to /ideas/ with pagination', async () => {
      mock.onGet('/ideas/?skip=10&limit=5').reply(200, []);
      const response = await ideas.getAll(10, 5);
      expect(response.data).toEqual([]);
    });

    it('getById should send GET to /ideas/{id}', async () => {
      mock.onGet('/ideas/1').reply(200, { id: 1 });
      const response = await ideas.getById(1);
      expect(response.data.id).toEqual(1);
    });

    it('update should send PUT to /ideas/{id}', async () => {
      const updateData = { title: 'Updated' };
      mock.onPut('/ideas/1').reply(200, updateData);

      const response = await ideas.update(1, updateData);
      expect(response.data).toEqual(updateData);
    });

    it('delete should send DELETE to /ideas/{id}', async () => {
      mock.onDelete('/ideas/1').reply(204);
      const response = await ideas.delete(1);
      expect(response.status).toEqual(204);
    });
  });

  describe('Analysis Service', () => {
    it('triggerAnalysis should send POST to /analysis/{id}/analyze', async () => {
      mock.onPost('/analysis/1/analyze').reply(202, { status: 'analyzing' });
      const response = await analysis.triggerAnalysis(1);
      expect(response.data.status).toEqual('analyzing');
    });

    it('getAnalysis should send GET to /analysis/{id}', async () => {
      mock.onGet('/analysis/1').reply(200, { overall_score: 8.5 });
      const response = await analysis.getAnalysis(1);
      expect(response.data.overall_score).toEqual(8.5);
    });

    it('getReport should send GET to /analysis/{id}/report', async () => {
      mock.onGet('/analysis/1/report').reply(200, { idea: {}, analysis: {} });
      const response = await analysis.getReport(1);
      expect(response.data).toHaveProperty('idea');
      expect(response.data).toHaveProperty('analysis');
    });
  });

  describe('Reports Service', () => {
    it('getPdfReport should send GET to /ideas/{id}/report/pdf', async () => {
      mock.onGet('/ideas/1/report/pdf').reply(200, new Blob());
      const response = await reports.getPdfReport(1);
      expect(response.status).toEqual(200);
    });

    it('getJsonReport should send GET to /ideas/{id}/report/json', async () => {
      mock.onGet('/ideas/1/report/json').reply(200, { id: 1 });
      const response = await reports.getJsonReport(1);
      expect(response.data.id).toEqual(1);
    });
  });

  describe('Dashboard Service', () => {
    it('getStats should send GET to /dashboard/stats', async () => {
      mock.onGet('/dashboard/stats').reply(200, { total_ideas: 5 });
      const response = await dashboard.getStats();
      expect(response.data.total_ideas).toEqual(5);
    });
  });

  describe('Interceptors', () => {
    beforeEach(() => {
      localStorage.clear();
      mock.resetHistory();
    });

    it('should add Authorization header if token exists in localStorage', async () => {
      localStorage.setItem('token', 'my-secret-token');
      mock.onGet('/test').reply(200);

      await api.get('/test');
      
      expect(mock.history.get[0].headers.Authorization).toEqual('Bearer my-secret-token');
    });

    it('should NOT add Authorization header if token missing', async () => {
      mock.onGet('/test').reply(200);

      await api.get('/test');
      
      expect(mock.history.get[0].headers.Authorization).toBeUndefined();
    });
  });
});
