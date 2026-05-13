<?php

namespace App\Tests\Controller;

use App\Controller\PurchaseController;
use PHPUnit\Framework\TestCase;
use Symfony\Component\HttpClient\MockHttpClient;
use Symfony\Component\HttpClient\Response\MockResponse;
use Symfony\Component\HttpFoundation\Response;

final class PurchaseControllerTest extends TestCase
{
    public function testIndexProxiesUpstreamPayload(): void
    {
        $client = new MockHttpClient([
            new MockResponse(json_encode([
                ['id' => 1, 'total' => 199.99],
            ], JSON_PRESERVE_ZERO_FRACTION), ['http_code' => 200]),
        ]);

        $controller = new PurchaseController($client, 'http://backend.test');
        $response = $controller->index();

        self::assertSame(Response::HTTP_OK, $response->getStatusCode());
        self::assertSame('application/json', $response->headers->get('Content-Type'));
        self::assertJsonStringEqualsJsonString(
            json_encode([
                ['id' => 1, 'total' => 199.99],
            ], JSON_PRESERVE_ZERO_FRACTION),
            $response->getContent()
        );
    }

    public function testIndexReturnsBadGatewayOnUpstreamFailure(): void
    {
        $client = new MockHttpClient([
            new MockResponse('', ['http_code' => 500]),
        ]);

        $controller = new PurchaseController($client, 'http://backend.test');
        $response = $controller->index();

        self::assertSame(Response::HTTP_BAD_GATEWAY, $response->getStatusCode());
    }
}
