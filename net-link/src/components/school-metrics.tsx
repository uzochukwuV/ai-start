
import React, { useEffect, useState } from "react";
import {Card, CardHeader, CardBody, CardFooter} from "@heroui/card";
import {
    Table,
    TableHeader,
    TableBody,
    TableColumn,
    TableRow,
    TableCell
  } from "@heroui/table";
import { Loader } from "lucide-react";

const TopSchools = ({route}:any) => {
  const [top_schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (top_schools.length > 1){
        setLoading(false);
        return 
    }

    const fetchTopSchools = async () => {
      try {
        const response = await fetch(`https://ominous-acorn-rx4vvjv44v9fxp9-5000.app.github.dev/${route}`);
        if (!response.ok) {
          throw new Error("Failed to fetch top schools");
        }
        const data = await response.json();
        console.log(data)
        setSchools(Object.values(data));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTopSchools();
  }, [top_schools]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader className="animate-spin" size={48} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen text-red-500">
        <p>Error: {error}</p>
      </div>
    );
  }
 
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">{route == "bottom_schools"? "Least":"Top"} School in Connectivity</h1>
      <Card>
        <CardBody>
          <Table>
            <TableHeader>
                <TableColumn>Rank</TableColumn>
                <TableColumn>School Name</TableColumn>
                <TableColumn>Performance Score</TableColumn>
            </TableHeader>
            <TableBody>
              {top_schools.map((school, index) => (
                <TableRow key={index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell className=" line-clamp-1 leading-7" >{school?.school_name_x}</TableCell>
                  <TableCell>{school?.connection_quality_score}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardBody>
      </Card>
    </div>
  );
};

export default TopSchools;
