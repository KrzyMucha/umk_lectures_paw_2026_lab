<?php

namespace App\EventSubscriber;

use App\Service\MetricsCollector;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

class MetricsSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly MetricsCollector $metrics,
    ) {}

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::RESPONSE => 'onResponse',
        ];
    }

    public function onResponse(ResponseEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        $response = $event->getResponse();

        // Skip /metrics itself to avoid self-counting noise
        $path = $request->getPathInfo();
        if ($path === '/metrics' || $path === '/metrics/') {
            return;
        }

        $this->metrics->track($path, $response->getStatusCode());
    }
}
