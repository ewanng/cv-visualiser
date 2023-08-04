<template>
  <!-- Utilised BootstrapVue components rows and cols for their ease of use to build a responsive interface -->
  <b-container fluid>
    <br />
    <!-- Top box containing Device selection, graph type selection, and first/second date pickers -->
    <b-row>
      <!-- Boostrap columns allow me to create sections in rows for putting in forms or other boxes -->
      <b-col cols="2"></b-col>
      <b-col cols="8">
        <b-card bg-variant="light">
          <b-form inline>
            <label class="ml-auto mr-3" for="deviceInput">Device ID:</label>
            <!-- Device ID selection menu that loads available reading dates once an ID is selected -->
            <b-form-select
              class="mr-auto"
              v-model="selectDeviceID"
              :options="activeDevices"
              @change="loadDeviceDates(selectDeviceID)"
              id="deviceInput"
            ></b-form-select>
            <label class="ml-auto mr-3" for="graphTypeInput">Graph Type:</label>
            <b-form-radio-group
              class="mr-auto"
              v-model="selectedGraphType"
              :options="typeOptions"
              id="graphTypeInput"
            ></b-form-radio-group>
          </b-form>
          <br />
          <!-- Displays two Date pickers if the Comparison graph type is selected, gets the max and min date from the loading of dates above -->
          <b-form inline v-if="this.selectedGraphType == 'Comparison'">
            <label class="ml-auto mr-3" for="firstDatePicker"
              >First Reading Date:</label
            >
            <b-form-datepicker
              class="mr-auto"
              v-model="firstSelectedDate"
              locale="en"
              :min="deviceDateMin"
              :max="deviceDateMax"
              id="firstDatePicker"
            ></b-form-datepicker>
            <label class="ml-auto mr-3" for="secondDatePicker"
              >Second Reading Date:</label
            >
            <b-form-datepicker
              class="mr-auto"
              v-model="secondSelectedDate"
              locale="en"
              :min="deviceDateMin"
              :max="deviceDateMax"
              id="secondDatePicker"
            ></b-form-datepicker>
          </b-form>
          <!-- If Individual graph type, display one date picker and get max and min dates in the same way -->
          <b-form inline v-if="this.selectedGraphType == 'Individual'">
            <label class="ml-auto mr-3" for="firstDatePicker"
              >Reading Date:</label
            >
            <b-form-datepicker
              class="mr-auto"
              v-model="firstSelectedDate"
              locale="en"
              :min="deviceDateMin"
              :max="deviceDateMax"
              id="firstDatePicker"
            ></b-form-datepicker>
          </b-form>
          <br />
          <b-row>
            <!-- Use the selected Device ID and first and/or second date to load reading times -->
            <b-button
              class="m-1 ml-auto"
              variant="info"
              v-on:click="
                loadCVReadings(
                  selectDeviceID,
                  firstSelectedDate,
                  secondSelectedDate
                )
              "
            >
              View Readings
            </b-button>
            <!-- Reset buttons which resets all selected fields in the form to nothing, clean slate for a new review -->
            <b-button
              class="m-1 mr-auto"
              variant="secondary"
              v-on:click="resetSelection()"
            >
              Reset
            </b-button>
          </b-row>
        </b-card>
      </b-col>
    </b-row>
    <br />
    <!-- Once reading times have been loaded,
      show the box below which contains either readings times or 
      No data if there are no times from selected date -->
    <div
      v-if="this.firstGraphReadings != null && this.secondGraphReadings != null"
    >
      <b-row v-if="this.selectedGraphType == 'Comparison'">
        <b-col cols="2"> </b-col>
        <b-col cols="8">
          <b-card>
            <div>
              <b-form-group
                v-if="
                  this.firstGraphGenerated == true &&
                  this.secondGraphGenerated == true
                "
                label="Comparison Mode:"
                v-slot="{ ariaDescribedby }"
              >
                <b-form-radio-group
                  v-model="selectedComparison"
                  :aria-describedby="ariaDescribedby"
                  :options="compOptions"
                  name="comp-inline"
                ></b-form-radio-group>
              </b-form-group>
              <hr />
            </div>
            <b-row>
              <b-col
                v-if="this.selectedComparison == 'Overlapped'"
                cols="3"
              ></b-col>
              <b-col v-if="this.selectedComparison == 'Overlapped'" cols="6"
                ><b-card
                  class="graphCard"
                  v-if="
                    this.firstGraphGenerated == true &&
                    this.secondGraphGenerated == true &&
                    this.selectedComparison == 'Overlapped'
                  "
                >
                  <b-row>
                    <b-col cols="10">
                      <p>
                        First Reading Time:
                        <b>{{ this.firstSelectedTime }}</b>
                        | Second Reading Time:
                        <b>{{ this.secondSelectedTime }}</b>
                      </p>
                    </b-col>
                    <b-col cols="2">
                      <b-button
                        v-on:click="
                          (firstGraphGenerated = false),
                            (secondGraphGenerated = false),
                            (selectedComparison = 'Side by Side')
                        "
                        variant="light"
                        class="backButton ml-0"
                        pill
                        size="sm"
                      >
                        <b-icon scale="0.7" icon="x-lg"></b-icon
                      ></b-button>
                    </b-col>
                  </b-row>
                  <ApexChart
                    width="100%"
                    type="line"
                    :options="chartOptions"
                    :series="overlappedSeries"
                  ></ApexChart>

                  <template #footer>
                    <div>
                      <b-button
                        class="m-1 ml-auto"
                        variant="info"
                        v-b-modal="'ovdata-modal1'"
                        >View First Data</b-button
                      >
                      <b-modal
                        id="ovdata-modal1"
                        scrollable
                        title="First Graph CV Data"
                      >
                        <b>Data Set 1</b>
                        <hr />
                        <p>{{ firstVoltageList.join(", ") }}</p>
                        <b>Data Set 2</b>
                        <hr />
                        <p>{{ firstCurrentList.join(", ") }}</p>
                      </b-modal>
                      <b-button
                        class="m-1 ml-auto"
                        variant="info"
                        v-b-modal="'ovdata-modal2'"
                        >View Second Data</b-button
                      >
                      <b-modal
                        id="ovdata-modal2"
                        scrollable
                        title="Second Graph CV Data"
                      >
                        <b>Data Set 1</b>
                        <hr />
                        <p>{{ secondVoltageList.join(", ") }}</p>
                        <b>Data Set 2</b>
                        <hr />
                        <p>{{ secondCurrentList.join(", ") }}</p>
                      </b-modal>
                    </div>
                  </template>
                </b-card></b-col
              >
              <b-col cols="6">
                <b-card
                  class="graphCard mx"
                  v-if="this.firstGraphReadings == 'No Data'"
                >
                  <p>No data available - Please select another date.</p>
                </b-card>
                <b-card
                  class="graphCard"
                  v-if="
                    (this.firstGraphGenerated == true &&
                      this.selectedComparison == 'Side by Side') ||
                    (this.firstGraphGenerated == true &&
                      this.secondGraphGenerated == false &&
                      this.selectedComparison == 'Overlapped')
                  "
                >
                  <b-row>
                    <b-col cols="10">
                      <p>
                        Reading Time:
                        <b>{{ this.firstSelectedTime }}</b>
                      </p>
                    </b-col>
                    <b-col cols="2">
                      <b-button
                        v-on:click="firstGraphGenerated = false"
                        variant="light"
                        class="backButton ml-0"
                        pill
                        size="sm"
                      >
                        <b-icon scale="0.7" icon="x-lg"></b-icon
                      ></b-button>
                    </b-col>
                  </b-row>
                  <ApexChart
                    width="100%"
                    type="line"
                    :options="chartOptions"
                    :series="series1"
                    :key="firstChartKey"
                  ></ApexChart>
                  <template #footer
                    ><b-button
                      class="ml-auto"
                      variant="info"
                      v-b-modal.data-modal1
                      >View Data</b-button
                    >

                    <b-modal
                      id="data-modal1"
                      scrollable
                      :hide-footer="hideFooter"
                      title="First Graph CV Data"
                    >
                      <b>Data Set 1</b>
                      <hr />
                      <p>{{ firstVoltageList.join(", ") }}</p>
                      <b>Data Set 2</b>
                      <hr />
                      <p>{{ firstCurrentList.join(", ") }}</p>
                    </b-modal>
                  </template>
                </b-card>
                <b-card
                  class="graphCard"
                  v-if="
                    this.firstGraphReadings != 'No Data' &&
                    this.firstGraphGenerated == false
                  "
                >
                  <template #footer>
                    <b-button
                      v-if="firstSelectedTime != ''"
                      variant="info"
                      v-on:click="generateFirstGraph()"
                      >Generate Graph</b-button
                    >
                    <b-button
                      v-if="firstSelectedTime == ''"
                      disabled
                      variant="info"
                      v-on:click="generateFirstGraph()"
                      >Generate Graph</b-button
                    ></template
                  >
                  <b-list-group class="overflow-auto list-group">
                    <b-list-group-item
                      button
                      v-on:click="timeSelectedFirst(time)"
                      v-for="time in this.formattedFirstDateReadings"
                      :key="time.time"
                      class="d-flex justify-content-between align-items-center"
                    >
                      {{ time.time }} Reading
                      <b-badge variant="info" v-if="time.selected == true" pill
                        >&#10003;</b-badge
                      >
                    </b-list-group-item>
                  </b-list-group>
                  <br />
                </b-card>
              </b-col>
              <b-col cols="6">
                <b-card
                  class="graphCard"
                  v-if="this.secondGraphReadings == 'No Data'"
                >
                  <p>No data available - Please select another date.</p>
                </b-card>
                <b-card
                  class="graphCard"
                  v-if="
                    (this.secondGraphGenerated == true &&
                      this.selectedComparison == 'Side by Side') ||
                    (this.firstGraphGenerated == false &&
                      this.secondGraphGenerated == true &&
                      this.selectedComparison == 'Overlapped')
                  "
                >
                  <b-row>
                    <b-col cols="10">
                      <p>
                        Reading Time:
                        <b>{{ this.secondSelectedTime }}</b>
                      </p>
                    </b-col>
                    <b-col cols="2">
                      <b-button
                        v-on:click="secondGraphGenerated = false"
                        variant="light"
                        class="backButton ml-0"
                        pill
                        size="sm"
                      >
                        <b-icon scale="0.7" icon="x-lg"></b-icon
                      ></b-button>
                    </b-col>
                  </b-row>
                  <ApexChart
                    width="100%"
                    type="line"
                    :options="chartOptions"
                    :series="series2"
                    :key="secondChartKey"
                  ></ApexChart>
                  <template #footer
                    ><b-button
                      class="ml-auto"
                      variant="info"
                      v-b-modal.data-modal2
                      >View Data</b-button
                    >
                    <b-modal
                      id="data-modal2"
                      scrollable
                      :hide-footer="hideFooter"
                      title="Second Graph CV Data"
                    >
                      <b>Data Set 1</b>
                      <hr />
                      <p>{{ secondVoltageList.join(", ") }}</p>
                      <b>Data Set 2</b>
                      <hr />
                      <p>{{ secondCurrentList.join(", ") }}</p>
                    </b-modal></template
                  >
                </b-card>
                <b-card
                  class="graphCard"
                  v-if="
                    this.secondGraphReadings != 'No Data' &&
                    this.secondGraphGenerated == false
                  "
                >
                  <template #footer>
                    <b-button
                      v-if="secondSelectedTime != ''"
                      variant="info"
                      v-on:click="generateSecondGraph()"
                      >Generate Graph</b-button
                    >
                    <b-button
                      v-if="secondSelectedTime == ''"
                      disabled
                      variant="info"
                      v-on:click="generateSecondGraph()"
                      >Generate Graph</b-button
                    >
                  </template>
                  <b-list-group class="overflow-auto list-group">
                    <b-list-group-item
                      button
                      v-on:click="timeSelectedSecond(time)"
                      v-for="time in this.formattedSecondDateReadings"
                      :key="time.time"
                      class="d-flex justify-content-between align-items-center"
                    >
                      {{ time.time }} Reading
                      <b-badge variant="info" v-if="time.selected == true" pill
                        >&#10003;</b-badge
                      >
                    </b-list-group-item>
                  </b-list-group>
                  <br />
                </b-card>
              </b-col>
              <b-col cols="2"> </b-col>
            </b-row>
          </b-card>
        </b-col>
      </b-row>
      <b-row v-if="this.selectedGraphType == 'Individual'">
        <b-col cols="2"> </b-col>
        <b-col cols="8">
          <b-card>
            <b-row>
              <b-col cols="3"></b-col>
              <b-col cols="6"
                ><b-card
                  class="graphCard"
                  v-if="this.firstGraphGenerated == true"
                >
                  <b-row>
                    <b-col cols="10">
                      <p>
                        Reading Time:
                        <b>{{ this.firstSelectedTime }}</b>
                      </p>
                    </b-col>
                    <b-col cols="2">
                      <b-button
                        v-on:click="firstGraphGenerated = false"
                        variant="light"
                        class="backButton ml-0"
                        pill
                        size="sm"
                      >
                        <b-icon scale="0.7" icon="x-lg"></b-icon
                      ></b-button>
                    </b-col>
                  </b-row>
                  <ApexChart
                    width="100%"
                    type="line"
                    :options="chartOptions"
                    :series="series1"
                  ></ApexChart>

                  <template #footer>
                    <div>
                      <b-button
                        class="m-1 ml-auto"
                        variant="info"
                        v-b-modal="'ovdata-modal1'"
                        >View Data</b-button
                      >
                      <b-modal id="ovdata-modal1" scrollable title="CV Data">
                        <b>Data Set 1</b>
                        <hr />
                        <p>{{ firstVoltageList.join(", ") }}</p>
                        <b>Data Set 2</b>
                        <hr />
                        <p>{{ firstCurrentList.join(", ") }}</p>
                      </b-modal>
                    </div>
                  </template>
                </b-card>
                <b-card
                  class="graphCard mx"
                  v-if="this.firstGraphReadings == 'No Data'"
                >
                  <p>No data available - Please select another date.</p>
                </b-card>

                <b-card
                  class="graphCard"
                  v-if="
                    this.firstGraphReadings != 'No Data' &&
                    this.firstGraphGenerated == false
                  "
                >
                  <template #footer>
                    <b-button
                      v-if="firstSelectedTime != ''"
                      variant="info"
                      v-on:click="generateFirstGraph()"
                      >Generate Graph</b-button
                    >
                    <b-button
                      v-if="firstSelectedTime == ''"
                      disabled
                      variant="info"
                      v-on:click="generateFirstGraph()"
                      >Generate Graph</b-button
                    ></template
                  >
                  <b-list-group class="overflow-auto list-group">
                    <b-list-group-item
                      button
                      v-on:click="timeSelectedFirst(time)"
                      v-for="time in this.formattedFirstDateReadings"
                      :key="time.time"
                      class="d-flex justify-content-between align-items-center"
                    >
                      {{ time.time }} Reading
                      <b-badge variant="info" v-if="time.selected == true" pill
                        >&#10003;</b-badge
                      >
                    </b-list-group-item>
                  </b-list-group>
                  <br />
                </b-card>
              </b-col>
            </b-row>
          </b-card>
        </b-col>
      </b-row>
    </div>
  </b-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      hideFooter: true,
      deviceDateMin: "",
      deviceDateMax: "",
      firstChartKey: 0,
      secondChartKey: 0,
      firstSelectedDate: "",
      secondSelectedDate: "",
      firstSelectedTime: "",
      secondSelectedTime: "",
      firstGraphGenerated: false,
      secondGraphGenerated: false,
      firstVoltageList: [],
      firstCurrentList: [],
      formattedFirstDateReadings: [],
      formattedSecondDateReadings: [],
      formattedFirstCv: [],
      formattedSecondCv: [],
      currentList: [],
      voltageList: [],
      firstGraphReadings: null,
      secondGraphReadings: null,
      selectDeviceID: "Placeholder",
      selectedComparison: "Side by Side",
      selectedGraphType: "Individual",
      activeDevices: [],
      compOptions: [
        { text: "Side by Side", value: "Side by Side" },
        { text: "Overlapped", value: "Overlapped" },
      ],
      typeOptions: [
        { text: "Individual", value: "Individual" },
        { text: "Comparison", value: "Comparison" },
      ],
      chartOptions: {
        stroke: {
          curve: "smooth",
          width: "1",
        },
        chart: {
          id: "CV-Chart",
        },
        xaxis: {
          type: "numeric",
          tickAmount: 5,
          decimalsInFloat: 1,
        },
      },
      series1: [
        {
          name: "first_cv_data",
          data: [],
        },
      ],
      series2: [
        {
          name: "second_cv_data",
          data: [],
        },
      ],
      overlappedSeries: [
        {
          name: "first_cv_data",
          data: [],
        },
        {
          name: "second_cv_data",
          data: [],
        },
      ],
    };
  },
  mounted() {
    let lookUpUrlActiveDevices = this.$apiUrl + this.$apiEnv + "/visualiser";
    let lookUpHeadersActiveDevices = {
      headers: {
        "Content-Type": "application/json",
        "x-api-key": this.$apiKey,
      },
    };
    let lookUpRequestActiveDevices = {
      RequestType: "ActiveDevices",
      DataDict: [
        {
          DeviceID: "",
          ReadingDate: "",
        },
      ],
    };
    axios
      .post(
        lookUpUrlActiveDevices,
        lookUpRequestActiveDevices,
        lookUpHeadersActiveDevices
      )
      .then((response) => {
        this.activeDevices = [
          { text: "Please select a Device ID", value: "Placeholder" },
        ];
        for (let i = 0; i < response.data.Values.length; i++) {
          this.activeDevices.push({
            text: response.data.Values[i],
            value: response.data.Values[i],
          });
        }
      });
  },
  methods: {
    loadDeviceDates(device_id) {
      (this.firstSelectedDate = ""),
        (this.secondSelectedDate = ""),
        (this.firstSelectedTime = ""),
        (this.secondSelectedTime = ""),
        (this.firstGraphGenerated = false),
        (this.secondGraphGenerated = false),
        (this.firstVoltageList = []),
        (this.firstCurrentList = []),
        (this.formattedFirstDateReadings = []),
        (this.formattedSecondDateReadings = []),
        (this.formattedFirstCv = []),
        (this.formattedSecondCv = []),
        (this.currentList = []),
        (this.voltageList = []),
        (this.firstGraphReadings = null),
        (this.secondGraphReadings = null),
        (this.deviceDateMin = ""),
        (this.deviceDateMax = ""),
        (this.selectedComparison = "Side by Side");
      let lookUpUrlDeviceDates = this.$apiUrl + this.$apiEnv + "/visualiser";
      let lookUpHeadersDeviceDates = {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.$apiKey,
        },
      };
      let lookUpRequestDeviceDates = {
        RequestType: "LoadDeviceDates",
        DataDict: [
          {
            DeviceID: device_id,
          },
        ],
      };
      axios
        .post(
          lookUpUrlDeviceDates,
          lookUpRequestDeviceDates,
          lookUpHeadersDeviceDates
        )
        .then((response) => {
          this.deviceDateMin = response.data.Values[0][0];
          this.deviceDateMax = response.data.Values[0][1];
          this.deviceReadingDates = response.data.ReadingDates;
        });
    },
    generateFirstGraph() {
      let lookUpUrlFirstCVData = this.$apiUrl + this.$apiEnv + "/visualiser";
      let lookUpHeadersFirstCVData = {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.$apiKey,
        },
      };
      let lookUpRequestFirstCVData = {
        RequestType: "LoadCVData",
        DataDict: [
          {
            DeviceID: this.selectDeviceID,
            ReadingDate: this.firstSelectedDate,
            ReadingTime: this.firstSelectedTime,
          },
        ],
      };
      axios
        .post(
          lookUpUrlFirstCVData,
          lookUpRequestFirstCVData,
          lookUpHeadersFirstCVData
        )
        .then((response) => {
          console.log(response);
          this.firstVoltageList = response.data.VoltageList;
          this.firstCurrentList = response.data.CurrentList;
          this.formatCV(this.firstVoltageList, this.firstCurrentList);
          this.firstChartKey += 1;
          this.firstGraphGenerated = true;
        });
    },
    generateSecondGraph() {
      let lookUpUrlSecondCVData = this.$apiUrl + this.$apiEnv + "/visualiser";
      let lookUpHeadersSecondCVData = {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.$apiKey,
        },
      };
      let lookUpRequestSecondCVData = {
        RequestType: "LoadCVData",
        DataDict: [
          {
            DeviceID: this.selectDeviceID,
            ReadingDate: this.secondSelectedDate,
            ReadingTime: this.secondSelectedTime,
          },
        ],
      };
      axios
        .post(
          lookUpUrlSecondCVData,
          lookUpRequestSecondCVData,
          lookUpHeadersSecondCVData
        )
        .then((response) => {
          this.secondVoltageList = response.data.VoltageList;
          this.secondCurrentList = response.data.CurrentList;
          this.formatCV2(this.secondVoltageList, this.secondCurrentList);
          this.secondChartKey += 1;
          this.secondGraphGenerated = true;
        });
    },
    timeSelectedFirst(time) {
      this.firstSelectedTime = "";
      for (let i = 0; i < this.firstGraphReadings.length; i++) {
        if (this.formattedFirstDateReadings[i].time == time.time) {
          this.formattedFirstDateReadings[i].selected = true;
          this.firstSelectedTime = this.formattedFirstDateReadings[i].time;
        } else {
          this.formattedFirstDateReadings[i].selected = false;
        }
      }
    },
    timeSelectedSecond(time) {
      for (let i = 0; i < this.secondGraphReadings.length; i++) {
        if (this.formattedSecondDateReadings[i].time == time.time) {
          this.formattedSecondDateReadings[i].selected = true;
          this.secondSelectedTime = this.formattedSecondDateReadings[i].time;
        } else {
          this.formattedSecondDateReadings[i].selected = false;
        }
      }
    },
    resetSelection() {
      (this.firstSelectedDate = ""),
        (this.secondSelectedDate = ""),
        (this.firstSelectedTime = ""),
        (this.secondSelectedTime = ""),
        (this.firstGraphGenerated = false),
        (this.secondGraphGenerated = false),
        (this.firstVoltageList = []),
        (this.firstCurrentList = []),
        (this.formattedFirstDateReadings = []),
        (this.formattedSecondDateReadings = []),
        (this.formattedFirstCv = []),
        (this.formattedSecondCv = []),
        (this.currentList = []),
        (this.voltageList = []),
        (this.firstGraphReadings = null),
        (this.secondGraphReadings = null),
        (this.selectDeviceID = "Placeholder"),
        (this.deviceDateMin = ""),
        (this.deviceDateMax = ""),
        (this.selectedComparison = "Side by Side"),
        (this.selectedGraphType = "Individual");
    },
    loadCVReadings(deviceID, firstDate, secondDate) {
      (this.firstSelectedTime = ""),
        (this.secondSelectedTime = ""),
        (this.firstGraphGenerated = false),
        (this.secondGraphGenerated = false),
        (this.selectedComparison = "Side by Side"),
        (this.firstVoltageList = []),
        (this.firstCurrentList = []),
        (this.formattedFirstDateReadings = []),
        (this.formattedSecondDateReadings = []),
        (this.formattedFirstCv = []),
        (this.formattedSecondCv = []),
        (this.currentList = []),
        (this.voltageList = []),
        (this.firstGraphReadings = null),
        (this.secondGraphReadings = null);
      if (this.selectedGraphType == "Comparison") {
        if (firstDate == "" || secondDate == "") {
          alert(
            "Please Enter a Device ID, First Graph Date, and Second Graph Date to View Readings."
          );
          return;
        }
      } else if (this.selectedGraphType == "Individual") {
        if (firstDate == "") {
          alert(
            "Please Enter a Device ID and a Reading Date to View Readings."
          );
          return;
        }
      }
      let lookUpUrlCVReadings = this.$apiUrl + this.$apiEnv + "/visualiser";
      let lookUpHeadersCVReadings = {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": this.$apiKey,
        },
      };
      let lookUpRequestCVReadings = {
        RequestType: "LoadCVReadingTimes",
        DataDict: [
          {
            DeviceID: deviceID,
            FirstDate: firstDate,
            SecondDate: secondDate,
          },
        ],
      };
      axios
        .post(
          lookUpUrlCVReadings,
          lookUpRequestCVReadings,
          lookUpHeadersCVReadings
        )
        .then((response) => {
          console.log(lookUpRequestCVReadings);
          console.log(response);
          if (response.data.statusCode != 400) {
            this.formattedFirstDateReadings = [];
            this.formattedSecondDateReadings = [];
            this.firstGraphReadings = [];
            this.secondGraphReadings = [];
            if (response.data.FirstDateReadings.length == 0) {
              this.firstGraphReadings = "No Data";
            } else {
              this.firstGraphReadings = response.data.FirstDateReadings;
            }
            if (response.data.SecondDateReadings.length == 0) {
              this.secondGraphReadings = "No Data";
            } else {
              this.secondGraphReadings = response.data.SecondDateReadings;
            }
            if (this.firstGraphReadings != "No Data") {
              for (let i = 0; i < this.firstGraphReadings.length; i++) {
                this.formattedFirstDateReadings.push({
                  time: this.firstGraphReadings[i][0],
                  selected: false,
                });
              }
            }
            if (this.secondGraphReadings != "No Data") {
              for (let i = 0; i < this.secondGraphReadings.length; i++) {
                this.formattedSecondDateReadings.push({
                  time: this.secondGraphReadings[i][0],
                  selected: false,
                });
              }
            }
          }
          this.firstGraphGenerated = false;
          this.secondGraphGenerated = false;
        });
    },
    formatCV(voltageList, currentList) {
      this.voltageList = voltageList;
      this.currentList = currentList;
      this.formattedFirstCv = [];
      for (let i = 0; i < this.voltageList.length; i++) {
        this.formattedFirstCv.push({
          x: this.voltageList[i],
          y: this.currentList[i],
        });
      }
      this.series1 = [
        {
          name: "first_cv_data",
          data: this.formattedFirstCv,
        },
      ];
      this.overlappedSeries = [
        {
          name: "first_cv_data",
          data: this.formattedFirstCv,
        },
        {
          name: "second_cv_data",
          data: this.formattedSecondCv,
        },
      ];
    },
    formatCV2(voltageList, currentList) {
      this.voltageList = voltageList;
      this.currentList = currentList;
      this.formattedSecondCv = [];
      for (let i = 0; i < this.voltageList.length; i++) {
        this.formattedSecondCv.push({
          x: this.voltageList[i],
          y: this.currentList[i],
        });
      }
      this.series2 = [
        {
          name: "second_cv_data",
          data: this.formattedSecondCv,
        },
      ];
      this.overlappedSeries = [
        {
          name: "first_cv_data",
          data: this.formattedFirstCv,
        },
        {
          name: "second_cv_data",
          data: this.formattedSecondCv,
        },
      ];
    },
  },
};
</script>

<style></style>
