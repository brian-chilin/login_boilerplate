port ENV.fetch("PORT") { 80 }
environment ENV.fetch("RACK_ENV") { "production" }
workers ENV.fetch("WEB_CONCURRENCY") { 2 }
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count
preload_app!
