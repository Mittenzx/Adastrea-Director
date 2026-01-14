// Copyright (c) 2025 Mittenzx. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "HAL/Platform.h"
#include "Misc/Paths.h"
#include "HAL/PlatformProcess.h"

/**
 * Manages the Python subprocess for the Adastrea Director backend.
 * Handles starting, stopping, and monitoring the Python process lifecycle.
 * 
 * ⚠️ LEGACY COMPONENT - SCHEDULED FOR REMOVAL
 * 
 * This component is part of the old IPC-based architecture and is maintained for
 * parallel operation during the transition to the VibeUE architecture.
 * 
 * The VibeUE architecture uses AdastreaScriptService (IPythonScriptPlugin) for
 * in-process Python execution, eliminating the need for external processes.
 * 
 * This component will be removed in Phase 4 cleanup after full migration validation.
 * See ARCHITECTURE.md for details on the new architecture.
 * 
 * @deprecated Use AdastreaScriptService instead for Python execution.
 */
class ADASTREADIRECTOR_API FPythonProcessManager
{
public:
	FPythonProcessManager();
	~FPythonProcessManager();

	/**
	 * Starts the Python backend subprocess.
	 * @param PythonExecutablePath Path to the Python executable (python.exe or python3)
	 * @param BackendScriptPath Path to the IPC server script
	 * @param Port Port number for IPC communication
	 * @return true if the process was started successfully
	 */
	bool StartPythonProcess(const FString& PythonExecutablePath, const FString& BackendScriptPath, int32 Port);

	/**
	 * Stops the Python backend subprocess gracefully.
	 */
	void StopPythonProcess();

	/**
	 * Checks if the Python process is currently running.
	 * @return true if the process is running
	 */
	bool IsProcessRunning() const;

	/**
	 * Gets the process ID of the Python subprocess.
	 * @return Process ID, or 0 if not running
	 */
	uint32 GetProcessId() const;

	/**
	 * Restarts the Python process (stops then starts).
	 * @return true if restart was successful
	 */
	bool RestartProcess();

private:
	/** Handle to the Python process */
	FProcHandle ProcessHandle;

	/** Process ID */
	uint32 ProcessId;

	/** Paths and parameters used to start the process */
	FString PythonPath;
	FString ScriptPath;
	int32 IPCPort;

	/** Helper function to verify process is still alive */
	bool VerifyProcessAlive() const;
};
