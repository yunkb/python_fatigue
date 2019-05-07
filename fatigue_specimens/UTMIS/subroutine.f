      MODULE DATA_MOD
            REAL, DIMENSION(:, :), ALLOCATABLE :: STRESS_DATA
            REAL, DIMENSION(:, :), ALLOCATABLE :: HARDENING_DATA
      END MODULE DATA_MOD

      SUBROUTINE UEXTERNALDB(LOP,LRESTART,TIME,DTIME,KSTEP,KINC)
C
      USE DATA_MOD
      INCLUDE 'ABA_PARAM.INC'
C
      INTEGER N_LINES
      CHARACTER STRESS_FNAME*150
      DIMENSION TIME(2)
C
      IF (LOP .EQ. 0) THEN
        STRESS_FNAME = '/scratch/users/erik/scania_gear_analysis/' //
     1 'abaqus/utmis_specimens/residual_stresses_pos.dat'
        OPEN(15, FILE=TRIM(ADJUSTL(STRESS_FNAME)))
C     Find out the number of data lines
         N_LINES = 0
         DO
            READ(15, FMT=*, IOSTAT=IO)
            IF (IO /= 0) EXIT
            N_LINES = N_LINES + 1
         END DO
         REWIND(15)
         ALLOCATE(STRESS_DATA(N_LINES, 8))
         DO i=1, N_LINES
            READ(15, FMT=*) STRESS_DATA(i, :)
         END DO
         CLOSE(15)
        END IF
      RETURN
      END

      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,NAMES)
C
      USE DATA_MOD
      INCLUDE 'ABA_PARAM.INC'
C
      REAL s11, s22, s33, s12, s13, s23

      INTEGER ELEM_NUMBER, INTPOINTS, JRCD, ROW
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
C
      CHARACTER NAMES(2)*80
C
      CHARACTER INSTANCE*80
C
C user coding to define SIGMA(NTENS)
      s11 = 0.
      s22 = 0.
      s33 = 0.
      s12 = 0.
      s13 = 0.
      s23 = 0.
      INTPOINTS = 8
      CALL MutexLock(1)
      CALL GETPARTINFO(NOEL, 1, INSTANCE, ELEM_NUMBER, JRCD)
      CALL MutexUnlock(1)
      IF (JRCD .EQ. 0) THEN
         IF (INSTANCE .EQ. 'SPECIMEN_PART_POS') THEN
            ROW = (ELEM_NUMBER-1)*INTPOINTS + NPT
         ELSE
            IF (NPT .GT. 4) THEN
               ROW = (ELEM_NUMBER-1)*INTPOINTS + NPT - 4
            ELSE
               ROW = (ELEM_NUMBER-1)*INTPOINTS + NPT + 4
            END IF
         END IF
            s11 = STRESS_DATA(ROW, 3)
            s22 = STRESS_DATA(ROW, 4)
            s33 = STRESS_DATA(ROW, 5)
            s12 = STRESS_DATA(ROW, 6)
            s13 = STRESS_DATA(ROW, 7)
            s23 = STRESS_DATA(ROW, 8)
      END IF
      SIGMA(1) = s11
      SIGMA(2) = s22
      SIGMA(3) = s33
      SIGMA(4) = s12
      SIGMA(5) = s13
      SIGMA(6) = s23
      RETURN
      END

      SUBROUTINE UFIELD(FIELD,KFIELD,NSECPT,KSTEP,KINC,TIME,NODE,
     1 COORDS,TEMP,DTEMP,NFIELD)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FIELD(NSECPT,NFIELD), TIME(2), COORDS(3),
     1 TEMP(NSECPT), DTEMP(NSECPT)
C




      RETURN
      END

