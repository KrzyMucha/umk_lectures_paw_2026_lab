<?php

namespace App\Service;

use Psr\Cache\CacheItemPoolInterface;
use Symfony\Component\DependencyInjection\Attribute\Autowire;

class MetricsCollector
{
    private const TTL = 86400; // 24h

    public function __construct(
        #[Autowire(service: 'cache.app')]
        private readonly CacheItemPoolInterface $cache,
    ) {}

    /**
     * @return list<array{endpoint: string, status_code: int, count: int}>
     */
    public function getAll(): array
    {
        $indexItem = $this->cache->getItem('metrics_index');
        $index = $indexItem->isHit() ? (array) $indexItem->get() : [];

        $result = [];
        foreach ($index as $entry) {
            $item = $this->cache->getItem($entry['key']);
            if ($item->isHit()) {
                $result[] = [
                    'endpoint'    => $entry['endpoint'],
                    'status_code' => $entry['status_code'],
                    'count'       => (int) $item->get(),
                ];
            }
        }

        return $result;
    }

    public function track(string $endpoint, int $statusCode): void
    {
        $key = $this->cacheKey($endpoint, $statusCode);

        $indexItem = $this->cache->getItem('metrics_index');
        $index = $indexItem->isHit() ? (array) $indexItem->get() : [];

        $exists = count(array_filter($index, fn(array $e) => $e['key'] === $key)) > 0;
        if (!$exists) {
            $index[] = ['key' => $key, 'endpoint' => $endpoint, 'status_code' => $statusCode];
            $indexItem->set($index);
            $indexItem->expiresAfter(self::TTL);
            $this->cache->save($indexItem);
        }

        $countItem = $this->cache->getItem($key);
        $countItem->set(($countItem->isHit() ? (int) $countItem->get() : 0) + 1);
        $countItem->expiresAfter(self::TTL);
        $this->cache->save($countItem);
    }

    private function cacheKey(string $endpoint, int $statusCode): string
    {
        $safe = preg_replace('/[^a-zA-Z0-9_\-]/', '_', ltrim($endpoint, '/'));

        return sprintf('http_requests_%s_%d', $safe ?: 'root', $statusCode);
    }
}
