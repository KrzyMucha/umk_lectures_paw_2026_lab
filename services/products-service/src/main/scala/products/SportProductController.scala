package products

import cats.effect.*
import io.circe.*
import io.circe.syntax.*
import org.http4s.*
import org.http4s.circe.jsonEncoder
import org.http4s.dsl.io.*

class SportProductController(repo: SportProductRepository, ollama: OllamaClient, gemini: Option[GeminiClient] = None):

  def getById(id: Long): IO[Response[IO]] =
    repo.findById(id).flatMap:
      case Some(p) => Ok(p.asJson)
      case None    => NotFound(Json.obj("error" -> Json.fromString(s"Product $id not found")))

  def findByName(name: String): IO[Response[IO]] =
    repo.findByNameSubstring(name).flatMap:
      case Nil     => NotFound(Json.obj("error" -> Json.fromString(s"No products matching '$name'")))
      case results => Ok(results.asJson)

  def listAll: IO[Response[IO]] =
    repo.findAll.flatMap(products => Ok(products.asJson))

  def search(q: String, limit: Int, model: String = "ollama"): IO[Response[IO]] =
    val (embedIO, findIO) = model match
      case "gemini" => gemini match
        case Some(g) => (g.embed(q), (emb: Vector[Float]) => repo.findSimilarGemini(emb, limit))
        case None    => return InternalServerError(Json.obj("error" -> Json.fromString("Gemini not configured: GEMINI_API_KEY missing")))
      case _ => (ollama.embed(q), (emb: Vector[Float]) => repo.findSimilar(emb, limit))
    embedIO.attempt.flatMap:
      case Left(err) => InternalServerError(Json.obj("error" -> Json.fromString(s"$model embed error: ${err.getMessage}")))
      case Right(embedding) if embedding.isEmpty => InternalServerError(Json.obj("error" -> Json.fromString(s"$model returned empty embedding")))
      case Right(embedding) => findIO(embedding).flatMap:
        case Nil     => NotFound(Json.obj("error" -> Json.fromString(s"No results for '$q'")))
        case results => Ok(results.asJson)

