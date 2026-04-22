<?php

namespace App\Service;

use Psr\Log\LoggerInterface;
use Throwable;
use Symfony\Contracts\HttpClient\Exception\TransportExceptionInterface;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class UserServiceClient
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly HttpClientInterface $httpClient,
        private readonly string $userServiceBaseUrl,
    ) {}

    /** @return array{payload: mixed, status: int} */
    public function getUsers(): array
    {
        return $this->request('GET', '/users');
    }

    /** @return array{payload: mixed, status: int} */
    public function getSuperUsers(): array
    {
        return $this->request('GET', '/users-super');
    }

    /** @return array{payload: mixed, status: int} */
    public function getUserById(int $userId): array
    {
        return $this->request('GET', sprintf('/user/%d', $userId));
    }

    /** @return array{payload: mixed, status: int} */
    public function createUser(string $rawPayload): array
    {
        return $this->request('POST', '/users', $rawPayload);
    }

    /** @return array{payload: mixed, status: int} */
    private function request(string $method, string $path, ?string $body = null): array
    {
        $url = rtrim($this->userServiceBaseUrl, '/') . $path;

        try {
            $response = $this->httpClient->request($method, $url, [
                'headers' => [
                    'Accept' => 'application/json',
                    'Content-Type' => 'application/json',
                ],
                'body' => $body,
                'timeout' => 10,
                'max_duration' => 10,
            ]);
        } catch (TransportExceptionInterface|Throwable $error) {
            $this->logger->error('User service call failed', [
                'url' => $url,
                'method' => $method,
                'error' => $error->getMessage(),
            ]);

            return [
                'payload' => ['error' => 'User service unavailable'],
                'status' => 502,
            ];
        }

        $statusCode = $response->getStatusCode();
        $rawResponse = $response->getContent(false);

        $decoded = json_decode($rawResponse, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            $this->logger->warning('User service returned non-JSON response', [
                'url' => $url,
                'method' => $method,
                'status' => $statusCode,
            ]);

            return [
                'payload' => ['error' => 'Invalid response from user service'],
                'status' => 502,
            ];
        }

        return [
            'payload' => $decoded,
            'status' => $statusCode,
        ];
    }
}
