QSPI storage
============

.. contents:: :local:

Boards that ship with QSPI flash (the Adafruit CLUE has a 2 MiB GD25Q16) expose
it through four Board-domain commands. The flash is *adopted* on first use: an
adoption transaction erases the chip and writes a journal header that the
firmware then uses to log calibration payloads, runtime preferences, and any
other state the application asks to persist.

The four connector methods mirror the four protocol commands.


Querying the storage state
--------------------------

:func:`whad.board.BoardConnector.storage_info` returns a ``StorageInfoResponse``
with the current adoption state, total capacity in bytes, and the number of log
records currently held in the journal.

.. code-block:: python

    info = board.storage_info()
    print(info.state)            # 1 = NOT_ADOPTED, 2 = ADOPTED, 3 = ERASING
    print(info.capacity_bytes)
    print(info.log_record_count)

Adoption must succeed before any calibration can be persisted; if the storage
is not adopted, ``calibrate_imu(persist=True)`` silently stores nothing.


Adopting the storage
--------------------

:func:`~whad.board.BoardConnector.storage_adopt` performs the one-shot adoption
transaction. It requires a ``confirm_nonce`` integer (any non-zero value) to
make the destructive intent explicit at the protocol layer; the connector
additionally requires the caller to pass it. The transaction erases the chip.

.. code-block:: python

    response = board.storage_adopt(confirm_nonce=1)
    print(response.result)       # 0 = SUCCESS

After a successful adoption, ``storage_info()`` reports ``ADOPTED`` and the
journal is ready to accept records.


Reading the log
---------------

:func:`~whad.board.BoardConnector.storage_read_log` returns one ``LogChunk``
per call. The protocol is cursor-based: each chunk carries the next cursor,
the byte offset within the log, and a record count, plus an ``eof`` flag. The
convenience generator
:func:`~whad.board.BoardConnector.storage_read_log_all` walks the whole log
for you:

.. code-block:: python

    for chunk in board.storage_read_log_all(max_bytes=256):
        print(chunk.offset, chunk.count, chunk.data)
        if chunk.eof:
            break


Erasing the log
---------------

:func:`~whad.board.BoardConnector.storage_erase_log` begins an erase
transaction. Like adoption, it takes a ``confirm_nonce`` to signal destructive
intent. The erase itself runs asynchronously across firmware ``tick()`` calls;
the method returns as soon as the transaction is started. Poll
:func:`~whad.board.BoardConnector.storage_info` to know when the journal has
been fully erased.

.. code-block:: python

    response = board.storage_erase_log(confirm_nonce=1)
    print(response.result)       # 0 = SUCCESS (transaction started)
