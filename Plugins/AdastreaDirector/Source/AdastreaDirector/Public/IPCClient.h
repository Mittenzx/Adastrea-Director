// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "Interfaces/IPv4/IPv4Address.h"

/**
 * IPC client for communicating with the Python backend via TCP sockets.
 * Handles JSON request/response serialization and socket management.
 * 
 * ⚠️ LEGACY COMPONENT - SCHEDULED FOR REMOVAL
 * 
 * This component is part of the old IPC-based architecture and is maintained for
 * parallel operation during the transition to the VibeUE architecture.
 * 
 * The VibeUE architecture eliminates the need for IPC communication by using:
 * - AdastreaLLMClient for direct LLM API calls (no Python intermediary)
 * - AdastreaAssetService for runtime asset queries (no document ingestion)
 * - AdastreaScriptService for in-process Python execution
 * 
 * This component will be removed in Phase 4 cleanup after full migration validation.
 * See ARCHITECTURE.md for details on the new architecture.
 * 
 * @deprecated Use VibeUE components (AdastreaLLMClient, AdastreaAssetService) instead.
 */
class ADASTREADIRECTOR_API FIPCClient
{
public:
	FIPCClient();
	~FIPCClient();

	/**
	 * Connects to the Python IPC server.
	 * @param Host Host address (usually "127.0.0.1" for localhost)
	 * @param Port Port number to connect to
	 * @param TimeoutSeconds Connection timeout in seconds
	 * @return true if connection was successful
	 */
	bool Connect(const FString& Host, int32 Port, float TimeoutSeconds = 5.0f);

	/**
	 * Disconnects from the IPC server.
	 */
	void Disconnect();

	/**
	 * Checks if currently connected to the server.
	 * @return true if connected
	 */
	bool IsConnected() const;

	/**
	 * Sends a JSON request to the server and waits for a response.
	 * @param RequestJson JSON string to send
	 * @param OutResponse Response JSON string received from server
	 * @param TimeoutSeconds Timeout for receiving response
	 * @return true if request/response completed successfully
	 */
	bool SendRequest(const FString& RequestJson, FString& OutResponse, float TimeoutSeconds = 10.0f);

	/**
	 * Sends raw data to the server.
	 * @param Data Data to send
	 * @return true if send was successful
	 */
	bool Send(const TArray<uint8>& Data);

	/**
	 * Receives data from the server.
	 * @param OutData Buffer to receive data into
	 * @param TimeoutSeconds Timeout for receiving data
	 * @return true if receive was successful
	 */
	bool Receive(TArray<uint8>& OutData, float TimeoutSeconds = 10.0f);

private:
	/** Socket for communication */
	FSocket* Socket;

	/** Socket subsystem */
	ISocketSubsystem* SocketSubsystem;

	/** Connection address */
	TSharedPtr<FInternetAddr> ServerAddress;

	/** Helper to check if socket is still valid */
	bool IsSocketValid() const;

	/** Helper to wait for socket to be ready */
	bool WaitForSocket(float TimeoutSeconds, bool bWaitForRead) const;
};
