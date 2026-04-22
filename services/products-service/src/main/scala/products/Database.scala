package products

import cats.effect.*
import doobie.hikari.HikariTransactor

import java.net.URI

object Database:

  def transactor(databaseUrl: String): Resource[IO, HikariTransactor[IO]] =
    val jdbcUrl = toJdbcUrl(databaseUrl)
    HikariTransactor.newHikariTransactor[IO](
      driverClassName = "org.postgresql.Driver",
      url             = jdbcUrl,
      user            = "",
      pass            = "",
      connectEC       = scala.concurrent.ExecutionContext.global
    )

  private def toJdbcUrl(url: String): String =
    // postgresql://user:pass@host:port/dbname?params -> jdbc:postgresql://host:port/dbname
    val uri        = URI.create(url.replace("postgresql://", "http://"))
    val userInfo   = Option(uri.getUserInfo).getOrElse("")
    val (user, pw) = userInfo.split(":", 2) match
      case Array(u, p) => (u, p)
      case Array(u)    => (u, "")
      case _           => ("", "")
    val base = s"jdbc:postgresql://${uri.getHost}:${uri.getPort}${uri.getPath}"
    // przekaż user/password przez URL żeby uniknąć problemów z HikariCP i pustymi polami
    s"$base?user=$user&password=$pw"
