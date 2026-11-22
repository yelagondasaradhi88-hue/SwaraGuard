package com.swaraguard.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.GsonConverterFactory
import retrofit2 Retrofit

object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:8000"

    private var retrofit: Retrofit? = null

    fun createService(): SwaraGuardApi {
        val client = OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()

        retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        return retrofit!!.create(SwaraGuardApi::class.java)
    }
}