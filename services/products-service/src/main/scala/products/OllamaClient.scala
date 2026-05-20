package products

import cats.effect.*
import io.circe.parser.*
import io.circe.syntax.*

import java.net.URI
import java.net.http.{HttpClient as JHttpClient, HttpRequest, HttpResponse}

class OllamaClient(baseUrl: String = "http://localhost:11434"):
  private val http = JHttpClient.newHttpClient()

  def embed(text: String): IO[Vector[Float]] = IO.blocking:
    val body    = s"""{"model":"nomic-embed-text","prompt":${text.asJson}}"""
    val request = HttpRequest.newBuilder(URI.create(s"$baseUrl/api/embeddings"))
      .POST(HttpRequest.BodyPublishers.ofString(body))
      .header("Content-Type", "application/json")
      .build()
    val response = http.send(request, HttpResponse.BodyHandlers.ofString())
    parse(response.body()).toOption
      .flatMap(_.hcursor.downField("embedding").as[Vector[Float]].toOption)
      .getOrElse(Vector.empty)
