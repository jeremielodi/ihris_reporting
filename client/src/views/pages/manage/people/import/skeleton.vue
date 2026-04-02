<template>
    <div>
    <DataTable :value="Array(10).fill({})" scrollable showGridlines stripedRows resizableColumns scrollHeight="600px">
        <!-- INDEX -->
        <Column header="#" frozen>
            <template #body>
                <Skeleton size="2rem" />
            </template>
        </Column>

        <!-- STATUS -->
        <Column header="" frozen>
            <template #body>
                <Skeleton shape="circle" size="2rem" />
            </template>
        </Column>

        <!-- NOM -->
        <Column header="Nom & Prénom" frozen>
            <template #body>
                <Skeleton width="120px" />
            </template>
        </Column>

        <!-- MATRICULE -->
        <Column header="Matricule">
            <template #body>
                <Skeleton width="80px" />
            </template>
        </Column>

        <!-- SEXE -->
        <Column header="Sexe">
            <template #body>
                <Skeleton width="40px" />
            </template>
        </Column>

        <!-- DATE NAISSANCE -->
        <Column header="Date Naissance">
            <template #body>
                <Skeleton width="90px" />
            </template>
        </Column>

        <!-- LIEU -->
        <Column header="Lieu Naissance">
            <template #body>
                <Skeleton width="100px" />
            </template>
        </Column>

        <!-- ETAT CIVIL -->
        <Column header="Etat Civil">
            <template #body>
                <Skeleton width="80px" />
            </template>
        </Column>

        <!-- POSTE -->
        <Column header="Poste">
            <template #body>
                <Skeleton width="100px" />
            </template>
        </Column>

        <!-- CLASSIFICATION -->
        <Column header="Catégorie Professionnelle">
            <template #body>
                <Skeleton width="120px" />
            </template>
        </Column>

        <!-- JOB TYPE -->
        <Column header="Statut">
            <template #body>
                <Skeleton width="80px" />
            </template>
        </Column>

        <!-- SPECIALITE -->
        <Column header="Spécialité">
            <template #body>
                <Skeleton width="100px" />
            </template>
        </Column>

        <!-- GRADE -->
        <Column header="Grade">
            <template #body>
                <Skeleton width="60px" />
            </template>
        </Column>

        <!-- ECHELON -->
        <Column header="Echelon">
            <template #body>
                <Skeleton width="60px" />
            </template>
        </Column>

        <!-- ANCIEN POSTE -->
        <Column header="Ancien Poste">
            <template #body>
                <Skeleton width="100px" />
            </template>
        </Column>

        <!-- POSITION -->
        <Column header="Position actuelle">
            <template #body>
                <Skeleton width="120px" />
            </template>
        </Column>

        <!-- DATE INTEGRATION -->
        <Column header="Date Intégration">
            <template #body>
                <Skeleton width="90px" />
            </template>
        </Column>

        <!-- DATE SERVICE -->
        <Column header="Date Service">
            <template #body>
                <Skeleton width="90px" />
            </template>
        </Column>
    </DataTable>
    </div>
</template>
