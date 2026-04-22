<?php

declare(strict_types=1);

namespace App\Service;

use Symfony\Contracts\HttpClient\HttpClientInterface;

class ProductsServiceClient
{
    public function __construct(
        private readonly HttpClientInterface $httpClient,
        private readonly string $baseUrl,
    ) {}

    /**
     * @return array<int, array{id: int, name: string, description: string|null, price: float}>|null
     *         Returns null when the remote service is unavailable.
     */
    public function fetchProducts(): ?array
    {
        try {
            $response = $this->httpClient->request('GET', rtrim($this->baseUrl, '/') . '/products');
            return $response->toArray();
        } catch (\Throwable) {
            return null;
        }
    }
}
