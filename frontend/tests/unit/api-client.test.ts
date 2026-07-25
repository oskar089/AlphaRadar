import { describe, it, expect } from 'vitest'
import { apiClient, ApiClientError } from '@/lib/api-client'
import { http, HttpResponse } from 'msw'
import { server } from '../setup'

describe('apiClient', () => {
  describe('get', () => {
    it('returns JSON on success', async () => {
      const result = await apiClient.get<{ status: string }>('/api/health/live')
      expect(result).toEqual({ status: 'alive', version: '0.1.0' })
    })

    it('throws 404 with message', async () => {
      await expect(apiClient.get('/api/stocks/INVALID')).rejects.toThrow(ApiClientError)
      await expect(apiClient.get('/api/stocks/INVALID')).rejects.toMatchObject({ status: 404 })
    })
  })

  describe('error mapping', () => {
    it('maps 503 to service unavailable', async () => {
      server.use(
        http.get('/api/test', () => new HttpResponse(null, { status: 503 })),
      )
      try {
        await apiClient.get('/api/test')
        expect.fail('should have thrown')
      } catch (err) {
        expect(err).toBeInstanceOf(ApiClientError)
        expect((err as ApiClientError).status).toBe(503)
        expect((err as ApiClientError).message).toBe('Service Unavailable')
      }
    })

    it('maps 5xx to generic error', async () => {
      server.use(
        http.get('/api/test', () => new HttpResponse(null, { status: 500 })),
      )
      try {
        await apiClient.get('/api/test')
        expect.fail('should have thrown')
      } catch (err) {
        expect(err).toBeInstanceOf(ApiClientError)
        expect((err as ApiClientError).status).toBe(500)
        expect((err as ApiClientError).message).toBe('Internal server error')
      }
    })

    it('maps 422 to validation error', async () => {
      server.use(
        http.get('/api/test', () =>
          HttpResponse.json({ detail: 'Invalid input' }, { status: 422 }),
        ),
      )
      try {
        await apiClient.get('/api/test')
        expect.fail('should have thrown')
      } catch (err) {
        expect(err).toBeInstanceOf(ApiClientError)
        expect((err as ApiClientError).status).toBe(422)
        expect((err as ApiClientError).message).toBe('Invalid input')
      }
    })
  })

  describe('post', () => {
    it('sends JSON body and returns response', async () => {
      const result = await apiClient.post<{ id: number }>('/api/portfolio/positions', {
        symbol: 'MSFT',
        quantity: 5,
        avg_buy_price: 300,
      })
      expect(result).toHaveProperty('id')
    })
  })

  describe('delete', () => {
    it('succeeds on 204', async () => {
      await expect(apiClient.delete('/api/portfolio/positions/1')).resolves.toBeUndefined()
    })
  })
})
