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

    public function increment(string $endpoint, int $statusCode): void
    {
        $key = $this->key($endpoint, $statusCode);
        $item = $this->cache->getItem($key);
        $item->set(($item->isHit() ? (int) $item->get() : 0) + 1);
        $item->expiresAfter(self::TTL);
        $this->cache->save($item);
    }

    public function getAll(): array
    {
        $indexItem = $this->cache->getItem('metrics_index');
        $keys = $indexItem->isHit() ? (array) $indexItem->get() : [];

        $metrics = [];
        foreach ($keys as $key) {
            $item = $this->cache->getItem($key);
            if ($item->isHit()) {
                $metrics[$key] = (int) $item->get();
            }
        }

        return $metrics;
    }

    public function track(string $endpoint, int $statusCode): void
    {
        $key = $this->key($endpoint, $statusCode);

        $indexItem = $this->cache->getItem('metrics_index');
        $keys = $indexItem->isHit() ? (array) $indexItem->get() : [];

        if (!in_array($key, $keys, true)) {
            $keys[] = $key;
            $indexItem->set($keys);
            $indexItem->expiresAfter(self::TTL);
            $this->cache->save($indexItem);
        }

        $this->increment($endpoint, $statusCode);
    }

    private function key(string $endpoint, int $statusCode): string
    {
        $safe = preg_replace('/[^a-zA-Z0-9_\-]/', '_', ltrim($endpoint, '/'));

        return sprintf('http_requests_%s_%d', $safe ?: 'root', $statusCode);
    }
}
