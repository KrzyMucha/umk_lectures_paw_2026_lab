package products

import cats.effect.*
import io.circe.parser.*
import io.circe.syntax.*

import java.net.URI
import java.net.http.{HttpClient as JHttpClient, HttpRequest, HttpResponse}

class GeminiClient(apiKey: String, outputDim: Int = 768):
  private val http = JHttpClient.newHttpClient()
  private val url  = s"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=$apiKey"

  def embed(text: String): IO[Vector[Float]] = IO.blocking:
    val body = s"""{"model":"models/gemini-embedding-001","content":{"parts":[{"text":${text.asJson}}]},"outputDimensionality":$outputDim}"""
    val request = HttpRequest.newBuilder(URI.create(url))
      .POST(HttpRequest.BodyPublishers.ofString(body))
      .header("Content-Type", "application/json")
      .build()
    val response = http.send(request, HttpResponse.BodyHandlers.ofString())
    val json = parse(response.body()).toOption.getOrElse(throw RuntimeException(s"Gemini non-JSON response [${response.statusCode()}]: ${response.body().take(300)}"))
    json.hcursor.downField("embedding").downField("values").as[Vector[Float]]
      .getOrElse(throw RuntimeException(s"Gemini error [${response.statusCode()}] key=${apiKey.take(8)}...: ${response.body().take(300)}"))
